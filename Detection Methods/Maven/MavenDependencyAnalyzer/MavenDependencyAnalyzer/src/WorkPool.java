import java.io.*;
import java.util.LinkedList;

/**
 * Class that contains lines of work that can be retrieved
 * by WorkerThreads.
 */
public class WorkPool {
    private LinkedList<String> workPool;

    public WorkPool(String filename) throws IOException {
        createWorkPool(filename);
    }

    /**
     * Read the lines from a file and put them in a LinkedList.
     * @param filename file to read the lines from
     */
    private void createWorkPool(String filename) throws IOException {
        File inputFile = new File(filename);
        FileReader fileReader = new FileReader(inputFile);
        BufferedReader bufferedReader = new BufferedReader(fileReader);
        String line;
        this.workPool = new LinkedList<>();

        // put lines from file in the WorkPool
        while ((line = bufferedReader.readLine()) != null) {
            this.workPool.push(line);
        }
    }

    /**
     * Function to get work from the WorkPool. It is synchronized,
     * since multiple threads can access this function.
     * @return a line of work
     */
    synchronized String getWork() {
        if (this.workPool.size() == 0) {
            // no more work left
            return null;
        }
        return this.workPool.pop();
    }

    /**
     * Function to print the results of a line of work. It is
     * synchronized, since multiple threads can access this
     * function.
     * @param diffAmounts the amount of differences between two commits
     * @param diff the differences between two commits
     */
    synchronized void printResults(String diffAmounts, String diff) throws IOException {
        // write diffAmounts to diffAmounts.csv
        FileWriter fileWriterDiffAmounts = new FileWriter("./output/diffAmounts.csv", true);
        BufferedWriter bufferedWriterDiffAmounts = new BufferedWriter(fileWriterDiffAmounts);
        bufferedWriterDiffAmounts.write(diffAmounts);
        bufferedWriterDiffAmounts.close();

        // write diff to diff.txt
        FileWriter fileWriterDiff = new FileWriter("./output/diff.txt", true);
        BufferedWriter bufferedWriterDiff = new BufferedWriter(fileWriterDiff);
        bufferedWriterDiff.write(diff);
        bufferedWriterDiff.close();

        // write both to stdout to inform user
        System.out.print(diffAmounts + diff);
    }
}
