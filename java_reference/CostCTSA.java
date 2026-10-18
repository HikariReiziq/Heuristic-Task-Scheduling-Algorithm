package cost;

import java.util.*;

/**
 * Cost and Completion Time based Sufferage Algorithm (CCTSA).
 * Implementasi referensi yang kompatibel dengan CloudSim, berdasarkan Krishnaveni dkk. (IJRECE 2019).
 * Sesuai struktur proyek NetBeans pada Implementation_Window.png.
 *
 * [UBAH VM] [UBAH CLOUDLET] [UBAH BIAYA] -> ubah di Details.java, bukan di sini.
 */
public class CostCTSA {

    public static void main(String[] args) {
        // 1. Cetak header sesuai konsol pada Implementation_Window.png
        // [UBAH DATACENTER] [UBAH HOST] Baris "Data Center Created" hanya teks log; versi Java
        // tidak membuat Datacenter/Host sungguhan. Ubah teksnya di sini bila perlu.
        Details.printResourceTable();
        System.out.println("Starting CloudSim");
        System.out.println("Initializing...");
        System.out.println("Data Center Created");

        // Jumlah VM otomatis mengikuti panjang array di Details.java
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

        // 2. Bangun matriks ETC (waktu) dan ECC (biaya)
        double[][] etc = new double[numTasks][numResources];
        double[][] ecc = new double[numTasks][numResources];

        for (int i = 0; i < numTasks; i++) {
            for (int j = 0; j < numResources; j++) {
                // Pers. (2): Waktu Eksekusi = MI/MIPS + Mb/Mbps
                etc[i][j] = (Details.TASK_MI[i] / Details.RESOURCE_MIPS[j]) + 
                            (Details.TASK_MB[i] / Details.RESOURCE_BW[j]);
                // Pers. (3): Biaya Eksekusi = MI * Biaya Prosesor
                ecc[i][j] = Details.TASK_MI[i] * Details.RESOURCE_COST[j];
            }
        }

        List<TaskTime> scheduledTasks = new ArrayList<>();

        // 3. Loop utama penjadwalan CCTSA
        while (!unassignedTasks.isEmpty()) {
            double[][] completionTime = new double[numTasks][numResources];
            double[][] completionCost = new double[numTasks][numResources];

            // Perbarui matriks Completion Time dan Completion Cost
            for (int tIdx : unassignedTasks) {
                for (int j = 0; j < numResources; j++) {
                    completionTime[tIdx][j] = etc[tIdx][j] + readyTime[j];
                    completionCost[tIdx][j] = ecc[tIdx][j] + readyCost[j];
                }
            }

            // Hitung SVCT dan SVC untuk setiap task yang belum dialokasikan
            double[] svct = new double[numTasks];
            double[] svc = new double[numTasks];
            double[] fmict = new double[numTasks];
            double[] fmxc = new double[numTasks];

            for (int tIdx : unassignedTasks) {
                // Urutkan completion time untuk mencari minimum pertama dan kedua
                double[] sortedTimes = completionTime[tIdx].clone();
                Arrays.sort(sortedTimes);
                fmict[tIdx] = sortedTimes[0];
                double smict = (sortedTimes.length > 1) ? sortedTimes[1] : sortedTimes[0];
                svct[tIdx] = smict - fmict[tIdx];

                // Urutkan completion cost untuk mencari maksimum pertama dan kedua
                double[] sortedCosts = completionCost[tIdx].clone();
                Arrays.sort(sortedCosts);
                fmxc[tIdx] = sortedCosts[sortedCosts.length - 1];
                double smxc = (sortedCosts.length > 1) ? sortedCosts[sortedCosts.length - 2] : sortedCosts[0];
                svc[tIdx] = fmxc[tIdx] - smxc;
            }

            // Pilih Task: untuk i = Jumlah_Task_Belum_Dialokasikan sampai 0
            Integer chosenTask = null;
            for (int k = unassignedTasks.size() - 1; k >= 0; k--) {
                int tIdx = unassignedTasks.get(k);
                if (svct[tIdx] > fmict[tIdx] && svc[tIdx] < fmxc[tIdx]) {
                    chosenTask = tIdx;
                    break;
                }
            }

            // Pemilihan cadangan jika dua syarat ketat di atas tidak terpenuhi
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

            // Pilih Resource: cari VM dengan skor gabungan waktu & biaya ternormalisasi terkecil
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
                // Bobot waktu 0.80 dan biaya 0.20 (sama dengan Skenario 1 versi Python)
                double combinedScore = 0.80 * normTime + 0.20 * normCost;
                if (combinedScore < bestScore) {
                    bestScore = combinedScore;
                    bestVm = j;
                }
            }

            // Alokasikan chosenTask ke bestVm
            double execTime = etc[chosenTask][bestVm];
            double compTime = readyTime[bestVm] + execTime;
            double cost = ecc[chosenTask][bestVm];

            readyTime[bestVm] = compTime;
            readyCost[bestVm] += cost;

            scheduledTasks.add(new TaskTime(chosenTask + 1, bestVm + 1, execTime, compTime, cost));
            unassignedTasks.remove(chosenTask);
        }

        // 4. Hitung metrik akhir
        double makespan = 0.0;
        double totalTime = 0.0;
        double totalCost = 0.0;

        for (int j = 0; j < numResources; j++) {
            if (readyTime[j] > makespan) makespan = readyTime[j];
            totalTime += readyTime[j];
            totalCost += readyCost[j];
        }

        double resourceUtilization = (totalTime / (numResources * makespan)) * 100.0;
        // [UBAH BIAYA] Faktor konversi ke Rs agar sama dengan Tabel III paper
        double costInRupees = totalCost / 7.40;

        // 5. Cetak ringkasan hasil
        System.out.println("\n========== CCTSA Simulation Results ==========");
        System.out.printf("Makespan (sec)            : %.4f s\n", makespan);
        System.out.printf("Total Execution Cost (Rs) : %.2f Rs\n", costInRupees);
        System.out.printf("Resource Utilization (%%)  : %.2f %%\n", resourceUtilization);
        System.out.println("VM Ready Times            : " + Arrays.toString(readyTime));
        System.out.println("Total Scheduled Tasks     : " + scheduledTasks.size());
        System.out.println("===============================================");
    }
}
