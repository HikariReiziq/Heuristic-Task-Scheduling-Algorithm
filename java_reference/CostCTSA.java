package cost;

import java.util.*;

/**
 * Cost and Completion Time based Sufferage Algorithm (CCTSA).
 * CloudSim-compatible reference implementation based on Krishnaveni et al. (IJRECE 2019).
 * Matches the NetBeans project structure shown in Implementation_Window.png.
 */
public class CostCTSA {

    public static void main(String[] args) {
        // 1. Print header matching console in Implementation_Window.png
        Details.printResourceTable();
        System.out.println("Starting CloudSim");
        System.out.println("Initializing...");
        System.out.println("Data Center Created");

        int numResources = Details.RESOURCE_NAMES.length;
        for (int j = 0; j < numResources; j++) {
            System.out.println("VM " + (j + 1) + " is Created with " + 
                               (int)Details.RESOURCE_MIPS[j] + " (mips) and " + 
                               (int)Details.RESOURCE_BW[j] + " (bw)");
        }

        double[] readyTime = new double[numResources];
        double[] readyCost = new double[numResources];
        System.out.println("Readytime of machine " + Arrays.toString(readyTime));

        int numTasks = Details.TASK_NAMES.length;
        List<Integer> unassignedTasks = new ArrayList<>();
        for (int i = 0; i < numTasks; i++) {
            unassignedTasks.add(i);
        }
        System.out.println("Remaining tasks: " + unassignedTasks);

        // 2. Build ETC and Cost Matrices
        double[][] etc = new double[numTasks][numResources];
        double[][] ecc = new double[numTasks][numResources];

        for (int i = 0; i < numTasks; i++) {
            for (int j = 0; j < numResources; j++) {
                // Eq (2): Execution Time = MI/MIPS + Mb/Mbps
                etc[i][j] = (Details.TASK_MI[i] / Details.RESOURCE_MIPS[j]) + 
                            (Details.TASK_MB[i] / Details.RESOURCE_BW[j]);
                // Eq (3): Execution Cost = MI * Cost of Processor
                ecc[i][j] = Details.TASK_MI[i] * Details.RESOURCE_COST[j];
            }
        }

        List<TaskTime> scheduledTasks = new ArrayList<>();

        // 3. Main CCTSA Scheduling Loop
        while (!unassignedTasks.isEmpty()) {
            double[][] completionTime = new double[numTasks][numResources];
            double[][] completionCost = new double[numTasks][numResources];

            // Update Completion Time and Cost matrices
            for (int tIdx : unassignedTasks) {
                for (int j = 0; j < numResources; j++) {
                    completionTime[tIdx][j] = etc[tIdx][j] + readyTime[j];
                    completionCost[tIdx][j] = ecc[tIdx][j] + readyCost[j];
                }
            }

            // Calculate SVCT and SVC for each unassigned task
            double[] svct = new double[numTasks];
            double[] svc = new double[numTasks];
            double[] fmict = new double[numTasks];
            double[] fmxc = new double[numTasks];

            for (int tIdx : unassignedTasks) {
                // Sort completion times to find First and Second Minimum
                double[] sortedTimes = completionTime[tIdx].clone();
                Arrays.sort(sortedTimes);
                fmict[tIdx] = sortedTimes[0];
                double smict = (sortedTimes.length > 1) ? sortedTimes[1] : sortedTimes[0];
                svct[tIdx] = smict - fmict[tIdx];

                // Sort completion costs to find First and Second Maximum
                double[] sortedCosts = completionCost[tIdx].clone();
                Arrays.sort(sortedCosts);
                fmxc[tIdx] = sortedCosts[sortedCosts.length - 1];
                double smxc = (sortedCosts.length > 1) ? sortedCosts[sortedCosts.length - 2] : sortedCosts[0];
                svc[tIdx] = fmxc[tIdx] - smxc;
            }

            // Select Task: For i = Unassigned_Task_Count to 0
            Integer chosenTask = null;
            for (int k = unassignedTasks.size() - 1; k >= 0; k--) {
                int tIdx = unassignedTasks.get(k);
                if (svct[tIdx] > fmict[tIdx] && svc[tIdx] < fmxc[tIdx]) {
                    chosenTask = tIdx;
                    break;
                }
            }

            // Fallback selection if strict double-condition is not met
            if (chosenTask == null) {
                double maxSufferage = -1.0;
                for (int tIdx : unassignedTasks) {
                    double score = (svct[tIdx] / (fmict[tIdx] + 1e-9)) + (svc[tIdx] / (fmxc[tIdx] + 1e-9));
                    if (score > maxSufferage) {
                        maxSufferage = score;
                        chosenTask = tIdx;
                    }
                }
            }

            // Select Resource: Find VM that minimizes normalized time and cost
            int bestVm = 0;
            double bestScore = Double.MAX_VALUE;
            double maxCt = 0.0, maxCc = 0.0;
            for (int j = 0; j < numResources; j++) {
                if (completionTime[chosenTask][j] > maxCt) maxCt = completionTime[chosenTask][j];
                if (completionCost[chosenTask][j] > maxCc) maxCc = completionCost[chosenTask][j];
            }

            for (int j = 0; j < numResources; j++) {
                double normTime = (maxCt > 0) ? completionTime[chosenTask][j] / maxCt : 0;
                double normCost = (maxCc > 0) ? completionCost[chosenTask][j] / maxCc : 0;
                double combinedScore = 0.80 * normTime + 0.20 * normCost;
                if (combinedScore < bestScore) {
                    bestScore = combinedScore;
                    bestVm = j;
                }
            }

            // Assign chosenTask to bestVm
            double execTime = etc[chosenTask][bestVm];
            double compTime = readyTime[bestVm] + execTime;
            double cost = ecc[chosenTask][bestVm];

            readyTime[bestVm] = compTime;
            readyCost[bestVm] += cost;

            scheduledTasks.add(new TaskTime(chosenTask + 1, bestVm + 1, execTime, compTime, cost));
            unassignedTasks.remove(chosenTask);
        }

        // 4. Compute Final Metrics
        double makespan = 0.0;
        double totalTime = 0.0;
        double totalCost = 0.0;

        for (int j = 0; j < numResources; j++) {
            if (readyTime[j] > makespan) makespan = readyTime[j];
            totalTime += readyTime[j];
            totalCost += readyCost[j];
        }

        double resourceUtilization = (totalTime / (numResources * makespan)) * 100.0;
        double costInRupees = totalCost / 7.40;

        // 5. Output Summary Results
        System.out.println("\n========== CCTSA Simulation Results ==========");
        System.out.printf("Makespan (sec)            : %.4f s\n", makespan);
        System.out.printf("Total Execution Cost (Rs) : %.2f Rs\n", costInRupees);
        System.out.printf("Resource Utilization (%%)  : %.2f %%\n", resourceUtilization);
        System.out.println("VM Ready Times            : " + Arrays.toString(readyTime));
        System.out.println("Total Scheduled Tasks     : " + scheduledTasks.size());
        System.out.println("===============================================");
    }
}
