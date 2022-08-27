import java.io.*;
import java.util.LinkedList;

/**
 * Class that contains lines of work that can be retrieved
 * by a Worker.
 */
public class WorkPool {
    private LinkedList<String> workPool;
    private BufferedWriter bufferedWriter;

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

        FileWriter fileWriter = new FileWriter(Arguments.getOutputFile(), true);
        bufferedWriter = new BufferedWriter(fileWriter);
    }

    /**
     * Function to get work from the WorkPool.
     * @return a line of work
     */
    synchronized public String getWork() {
        if (this.workPool.size() == 0) {
            // no more work left
            return null;
        }
        // give user an update on how far along we are
        if (this.workPool.size() % 100 == 0)
            System.out.println("Work left: " + this.workPool.size());

        return this.workPool.pop();
    }


    /**
     * Prints the issue names and numbers that were found in the Git message.
     */
    synchronized public void writeResults(
            String child,
            String[] IDs)
            throws IOException, InterruptedException {

        bufferedWriter.write(child + "\n");
        for (String ID : IDs)
            bufferedWriter.write("    " + ID + '\n');
    }
}
