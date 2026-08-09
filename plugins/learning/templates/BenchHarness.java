import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.function.LongSupplier;

/**
 * Minimal in-JVM microbenchmark harness.
 *
 * Timing a `java` process from outside measures JVM startup and JIT warmup, which normally
 * dominate whatever is under test. Measurement has to happen inside the JVM, after the code
 * has been compiled by C2.
 *
 * This is deliberately NOT JMH. It handles the three failure modes that make naive JVM
 * timings actively wrong rather than merely noisy:
 *
 *   1. JIT warmup            - run warmup iterations until C2 has compiled the hot path
 *   2. Dead-code elimination - consume every result into a volatile sink
 *   3. Constant folding      - benchmarks must read non-final, non-constant state
 *
 * It does NOT handle: loop unrolling artefacts, OSR quirks, inlining differences between a
 * benchmark and its real call site, or GC effects across iterations. When a result actually
 * matters, confirm it with real JMH. Treat a difference under ~10% here as unresolved.
 *
 * Usage:
 *   BenchHarness.compare("baseline", () -> workA(), "candidate", () -> workB());
 *
 * Each lambda must RETURN a value derived from its work, so the sink can consume it.
 */
public final class BenchHarness {

    /** Volatile so the JIT cannot prove the stored values are unused and delete the work. */
    public static volatile long sink;

    private static final int DEFAULT_WARMUP_ITERS = 20_000;
    private static final int DEFAULT_MEASURE_REPS = 15;
    private static final int DEFAULT_OPS_PER_REP = 2_000;

    // Below this, our resolution is not good enough to claim a winner honestly.
    private static final double MIN_MEANINGFUL_EFFECT = 0.10;

    private BenchHarness() {}

    public static double[] measure(LongSupplier body, int warmupIters, int reps, int opsPerRep) {
        for (int i = 0; i < warmupIters; i++) {
            sink = body.getAsLong();
        }
        // A settling pause lets any warmup-triggered GC finish outside the measured window.
        try {
            Thread.sleep(50);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        double[] nsPerOp = new double[reps];
        for (int r = 0; r < reps; r++) {
            long t0 = System.nanoTime();
            for (int i = 0; i < opsPerRep; i++) {
                sink = body.getAsLong();
            }
            nsPerOp[r] = (System.nanoTime() - t0) / (double) opsPerRep;
        }
        return nsPerOp;
    }

    public static double[] measure(LongSupplier body) {
        return measure(body, DEFAULT_WARMUP_ITERS, DEFAULT_MEASURE_REPS, DEFAULT_OPS_PER_REP);
    }

    private static double median(double[] xs) {
        double[] s = xs.clone();
        Arrays.sort(s);
        int n = s.length;
        return (n % 2 == 1) ? s[n / 2] : (s[n / 2 - 1] + s[n / 2]) / 2.0;
    }

    /** Median absolute deviation: robust to the interference spike every run eventually hits. */
    private static double mad(double[] xs) {
        double med = median(xs);
        double[] dev = new double[xs.length];
        for (int i = 0; i < xs.length; i++) {
            dev[i] = Math.abs(xs[i] - med);
        }
        return median(dev);
    }

    public static void report(String name, double[] samples) {
        double med = median(samples);
        System.out.printf("%-20s median %9.2f ns/op   MAD %6.2f (%.1f%%)   min %9.2f%n",
                name, med, mad(samples), 100.0 * mad(samples) / med, Arrays.stream(samples).min().orElse(0));
    }

    /**
     * Run two variants interleaved and print an honest verdict.
     *
     * Interleaving matters: running all of A then all of B lets JIT state, GC timing and CPU
     * frequency drift accumulate against whichever ran second.
     */
    public static void compare(String nameA, LongSupplier a, String nameB, LongSupplier b) {
        measure(a, DEFAULT_WARMUP_ITERS, 3, DEFAULT_OPS_PER_REP);
        measure(b, DEFAULT_WARMUP_ITERS, 3, DEFAULT_OPS_PER_REP);

        List<Double> sa = new ArrayList<>();
        List<Double> sb = new ArrayList<>();
        for (int r = 0; r < DEFAULT_MEASURE_REPS; r++) {
            sa.add(measure(a, 0, 1, DEFAULT_OPS_PER_REP)[0]);
            sb.add(measure(b, 0, 1, DEFAULT_OPS_PER_REP)[0]);
        }

        double[] arrA = sa.stream().mapToDouble(Double::doubleValue).toArray();
        double[] arrB = sb.stream().mapToDouble(Double::doubleValue).toArray();
        report(nameA, arrA);
        report(nameB, arrB);

        double ma = median(arrA), mb = median(arrB);
        double rel = (mb - ma) / ma;
        double noise = (mad(arrA) / ma) + (mad(arrB) / mb);

        System.out.println();
        if (Math.abs(rel) < Math.max(MIN_MEANINGFUL_EFFECT, noise)) {
            System.out.printf("VERDICT: indistinguishable (%.1f%% difference, noise floor %.1f%%)%n",
                    rel * 100, Math.max(MIN_MEANINGFUL_EFFECT, noise) * 100);
        } else {
            System.out.printf("VERDICT: %s is faster (%s is %+.1f%% vs %s)%n",
                    rel > 0 ? nameA : nameB, nameB, rel * 100, nameA);
        }
        System.out.println("NOTE: not JMH. Confirm anything load-bearing with real JMH.");
    }
}
