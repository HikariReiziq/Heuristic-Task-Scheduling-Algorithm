package cost;

/**
 * Details class.
 * Holds specification parameters for Resources (R1-R3) and Tasks (T1-T10)
 * as defined in Table I and Table II of Krishnaveni et al. (IJRECE 2019).
 */
public class Details {

    // Table I: Resource Specifications
    public static final String[] RESOURCE_NAMES = {"R1", "R2", "R3"};
    public static final double[] RESOURCE_MIPS = {50.0, 100.0, 200.0};
    public static final double[] RESOURCE_BW = {100.0, 200.0, 250.0};
    public static final double[] RESOURCE_COST = {0.03, 0.12, 0.24};

    // Table II: Task Specifications
    public static final String[] TASK_NAMES = {"T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"};
    public static final double[] TASK_MI = {206.0, 50.0, 128.0, 69.0, 118.0, 112.0, 21.0, 200.0, 90.0, 45.0};
    public static final double[] TASK_MB = {44.0, 95.0, 64.0, 30.0, 59.0, 47.0, 39.0, 61.0, 23.0, 23.0};

    public static void printResourceTable() {
        System.out.println("------------------------------------");
        System.out.println("R_Id\tMI\tBW\tCost");
        for (int i = 0; i < RESOURCE_NAMES.length; i++) {
            System.out.println(RESOURCE_NAMES[i] + "\t" + (int)RESOURCE_MIPS[i] + "\t" + 
                               (int)RESOURCE_BW[i] + "\t" + RESOURCE_COST[i]);
        }
        System.out.println("------------------------------------");
    }
}
