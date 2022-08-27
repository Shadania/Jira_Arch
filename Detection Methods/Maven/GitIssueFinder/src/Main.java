import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;



/**
 * Class that contains the main function.
 */
public class Main {
    /**
     * Print all Git commit messages from commits in the input file.
     * @param args program arguments
     */
    public static void main(String[] args) throws IOException, InterruptedException {
        Arguments.setGitProgramLocation(args[1]);
        Arguments.setGitRepositoryLocation(args[2]);
        Arguments.setIssuePrefixes(args[3]);
        Arguments.setOutputFile("output.txt");

        // delete old output file to overwrite it
        File file = new File(Arguments.getOutputFile());
        file.delete();

        // create a pool of work from the input file
        WorkPool workPool = new WorkPool(args[0]);

        // create worker that pulls work from the WorkPool
        // Worker worker = new Worker(workPool);
        // worker.work();

        int numOfThreads = (Runtime.getRuntime().availableProcessors() + 1) / 2;
        List<Worker> workers = new ArrayList<Worker>();
        for (int i = 0; i < numOfThreads; i++) {
            Worker worker = new Worker(workPool);
            worker.start();
            workers.add(worker);
        }

        for (int i = 0; i < numOfThreads; i++) {
            workers.get(i).join();
        }

        System.out.println("Done");
    }
}
