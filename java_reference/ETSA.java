package cost;

import java.util.*;

/**
 * Execution Time based Sufferage Algorithm (ETSA).
 * Baseline algorithm by Krishnaveni & Sinthu Janita (Springer 2019).
 */
public class ETSA {

    public static void main(String[] args) {
        Details.printResourceTable();
        System.out.println("Starting ETSA Simulation...");

        int numResources = Details.RESOURCE_NAMES.length;
        double[] readyTime = new double[numResources];
        double[] readyCost = new double[numResources];

        int numTasks = Details.TASK_NAMES.length;
        List<Integer> unassignedTasks = new ArrayList<>();
        for (int i = 0; i < numTasks; i++) {
            unassignedTasks.add(i);
        }

        double[][] etc = new double[numTasks][numResources];
        double[][] ecc = new double[numTasks][numResources];

        for (int i = 0; i < numTasks; i++) {
            for (int j = 0; j < numResources; j++) {
                etc[i][j] = (Details.TASK_MI[i] / Details.RESOURCE_MIPS[j]) + 
                            (Details.TASK_MB[i] / Details.RESOURCE_BW[j]);
                ecc[i][j] = Details.TASK_MI[i] * Details.RESOURCE_COST[j];
            }
        }

        List<TaskTime> scheduledTasks = new ArrayList<>();

        while (!unassignedTasks.isEmpty()) {
            Integer bestTask = null;
            int bestVm = 0;
            double maxSufferage = -1.0;

            for (int tIdx : unassignedTasks) {
                double minCt = Double.MAX_VALUE;
                double secondMinCt = Double.MAX_VALUE;
                int minVm = 0;

                for (int j = 0; j < numResources; j++) {
                    double ct = etc[tIdx][j] + readyTime[j];
                    if (ct < minCt) {
                        secondMinCt = minCt;
                        minCt = ct;
                        minVm = j;
                    } else if (ct < secondMinCt) {
                        secondMinCt = ct;
                    }
                }

                double sufferage = secondMinCt - minCt;
                if (sufferage > maxSufferage) {
                    maxSufferage = sufferage;
                    bestTask = tIdx;
                    bestVm = minVm;
                }
            }

            if (bestTask == null) {
                bestTask = unassignedTasks.get(0);
            }

            double execTime = etc[bestTask][bestVm];
            double compTime = readyTime[bestVm] + execTime;
            double cost = ecc[bestTask][bestVm];

            readyTime[bestVm] = compTime;
            readyCost[bestVm] += cost;

            scheduledTasks.add(new TaskTime(bestTask + 1, bestVm + 1, execTime, compTime, cost));
            unassignedTasks.remove(bestTask);
        }

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

        System.out.println("\n========== ETSA Simulation Results ==========");
        System.out.printf("Makespan (sec)            : %.4f s\n", makespan);
        System.out.printf("Total Execution Cost (Rs) : %.2f Rs\n", costInRupees);
        System.out.printf("Resource Utilization (%%)  : %.2f %%\n", resourceUtilization);
        System.out.println("VM Ready Times            : " + Arrays.toString(readyTime));
        System.out.println("==============================================");
    }
}
