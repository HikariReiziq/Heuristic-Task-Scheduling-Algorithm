package cost;

/**
 * Struktur data TaskTime.
 * Sesuai struktur proyek NetBeans CloudSim pada Implementation_Window.png.
 * Menyimpan pemetaan task ke VM, waktu eksekusi, waktu selesai, dan biaya.
 */
public class TaskTime {
    private int taskId;
    private int vmId;
    private double executionTime;
    private double completionTime;
    private double executionCost;

    public TaskTime(int taskId, int vmId, double executionTime, double completionTime, double executionCost) {
        this.taskId = taskId;
        this.vmId = vmId;
        this.executionTime = executionTime;
        this.completionTime = completionTime;
        this.executionCost = executionCost;
    }

    public int getTaskId() {
        return taskId;
    }

    public int getVmId() {
        return vmId;
    }

    public double getExecutionTime() {
        return executionTime;
    }

    public double getCompletionTime() {
        return completionTime;
    }

    public double getExecutionCost() {
        return executionCost;
    }

    @Override
    public String toString() {
        return "TaskTime [Task=" + taskId + ", VM=" + vmId + 
               ", ExecTime=" + executionTime + ", CompTime=" + completionTime + 
               ", Cost=" + executionCost + "]";
    }
}
