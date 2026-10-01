package cost;

import java.util.*;

/**
 * Standard Sufferage Algorithm.
 * Classic heuristic benchmark from Maheswaran et al. (1999).
 */
public class Sufferage {

    public static void main(String[] args) {
        Details.printResourceTable();
        System.out.println("Starting Standard Sufferage Simulation...");

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

        while (!unassignedTasks.isEmpty()) {
            // Map each VM to candidate tasks and their sufferage
            Map<Integer, List<int[]>> vmProposals = new HashMap<>();
            for (int j = 0; j < numResources; j++) {
                vmProposals.put(j, new ArrayList<>());
            }

            Map<Integer, Double> taskSufferage = new HashMap<>();

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
                taskSufferage.put(tIdx, sufferage);
                vmProposals.get(minVm).add(new int[]{tIdx});
            }

            boolean assigned = false;
            for (int j = 0; j < numResources; j++) {
                List<int[]> proposals = vmProposals.get(j);
                if (proposals.isEmpty()) continue;

                // Pick task with highest sufferage for this VM
                int bestTask = proposals.get(0)[0];
                double maxSuf = taskSufferage.get(bestTask);
                for (int[] p : proposals) {
                    if (taskSufferage.get(p[0]) > maxSuf) {
                        maxSuf = taskSufferage.get(p[0]);
                        bestTask = p[0];
                    }
                }

                double execTime = etc[bestTask][j];
                readyTime[j] += execTime;
                readyCost[j] += ecc[bestTask][j];

                unassignedTasks.remove(Integer.valueOf(bestTask));
                assigned = true;
                break;
            }

            if (!assigned && !unassignedTasks.isEmpty()) {
                int fallbackTask = unassignedTasks.get(0);
                readyTime[0] += etc[fallbackTask][0];
                readyCost[0] += ecc[fallbackTask][0];
                unassignedTasks.remove(0);
            }
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

        System.out.println("\n========== Standard Sufferage Simulation Results ==========");
        System.out.printf("Makespan (sec)            : %.4f s\n", makespan);
        System.out.printf("Total Execution Cost (Rs) : %.2f Rs\n", costInRupees);
        System.out.printf("Resource Utilization (%%)  : %.2f %%\n", resourceUtilization);
        System.out.println("VM Ready Times            : " + Arrays.toString(readyTime));
        System.out.println("===========================================================");
    }
}
