import java.io.File;
import java.io.IOException;
import java.util.ArrayList;

/**
 * Class that can be used as a Thread to work for a WorkPool.
 */
public class WorkerThread extends Thread {
    private final WorkPool workPool;
    private final String workDirectory;

    public WorkerThread(WorkPool workPool, String workDirectory) {
        this.workPool = workPool;
        this.workDirectory = workDirectory;
    }

    /**
     * When run, the function works for a WorkPool.
     */
    @Override
    public void run() {
        // create working directory
        try {
            Directory.createGitDirectory(new File(this.workDirectory));
        } catch (Exception e) {
            e.printStackTrace();
        }

        // retrieve work from the WorkPool each iteration
        String work;
        while ((work = this.workPool.getWork()) != null) {
            // split work line into commits
            String[] commits = work.split(" ");
            if (commits.length != 2) {
                // wrong amount of commits
                continue;
            }

            // get child and parent commits
            String child = commits[0];
            String parent = commits[1];

            // convert child commit to Tag array
            ArrayList<Tag> childTags = new ArrayList<>();
            try {
                childTags = Commit.toTagArray(child, this.workDirectory + "/" + Arguments.getRepositoryName());
            } catch (Exception exception) {
                System.err.println("Exception while analyzing commit: " + child);
                exception.printStackTrace();
            }

            // convert parent commit to Tag array
            ArrayList<Tag> parentTags = new ArrayList<>();
            try {
                parentTags = Commit.toTagArray(parent, this.workDirectory + "/" + Arguments.getRepositoryName());
            } catch (Exception exception) {
                System.err.println("Exception while analyzing commit: " + child);
                exception.printStackTrace();
            }

            // check if one of the TagArrays is not created
            if (childTags == null || parentTags == null) {
                continue;
            }

            // print the result of the comparison of the two TagArrays
            StringBuilder diffAmounts = new StringBuilder();
            StringBuilder diff = new StringBuilder();

            diffAmounts.append(child).append(", ");
            diff.append(child).append("\n");

            TagArray.compare(childTags, parentTags, diffAmounts, diff);
            try {
                this.workPool.printResults(diffAmounts.toString(), diff.toString());
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
