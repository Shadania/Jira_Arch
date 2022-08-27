import java.io.*;
import java.util.ArrayList;
import java.util.List;

/**
 * Class that retrieves work from a WorkPool and processes it.
 */
public class Worker extends Thread {
    private final WorkPool workPool;

    public Worker(WorkPool workPool) {
        this.workPool = workPool;
    }


    /**
     * Function that retrieves work from the WorkPool
     * until it is empty.
     */
    @Override
    public void run() {
        // retrieve work from the WorkPool each iteration
        String work;
        while ((work = this.workPool.getWork()) != null) {
            // split work into commits
            String[] commits = work.split(" ");
            if (commits.length != 2) {
                // wrong amount of commits
                continue;
            }

            // get child commit
            String child = commits[0];

            // print commit hash to inform user that this commit is being processed
            // System.out.println(child);

            // create writer to write to the output file


            // write the commit hash and print issues of each prefix
            try {


                workPool.writeResults(child, GetIssueIDs(child));
            } catch (Exception e) {
                System.out.println("Exception caught while printing issue " + child);
            }

            /*
            bufferedWriter.write(child + "\n");
            for (String prefix : Arguments.getIssuePrefixes()) {
                BufferedReader bufferedReader = getGitMessageReader(child);
                printIssues(messageToStringArr(prefix, bufferedReader), prefix, bufferedWriter);
            }

            bufferedWriter.close();
            */
        }
    }

    private String[] GetIssueIDs(String child) throws IOException, InterruptedException {
        List<String> result = new ArrayList<String>();

        for (String prefix : Arguments.getIssuePrefixes()) {
            BufferedReader bufRead = getGitMessageReader(child);

            // first: convert commit message to a stringbuilder
            StringBuilder build = new StringBuilder();
            String line;
            while ((line = bufRead.readLine()) != null) {
                build.append(line);
            }
            String[] split = build.toString().split(prefix + '-');
            for (int i = 1; i < split.length; i++) {
                StringBuilder thisID = new StringBuilder(prefix + '-');
                for (int j = 0; j < split[i].length(); j++) {
                    char ch = split[i].charAt(j);
                    if (!Character.isDigit(ch)) {
                        // end of issue number
                        break;
                    }
                    thisID.append(ch);
                }
                result.add(thisID.toString());
            }
        }

        return result.toArray(new String[0]);
    }

    /**
     * Runs a shell command to retrieve the Git message that belongs to the given commitHash.
     * @param commitHash hash of the commit
     * @return BufferedReader that can read the message
     */
    private BufferedReader getGitMessageReader(String commitHash) throws InterruptedException, IOException {
        // start shell command and wait until it is done
        Process process = Runtime.getRuntime().exec(
                Arguments.getGitProgramLocation() + " -C \"" +
                        Arguments.getGitRepositoryLocation() + "\" log --format=%B -n 1 " + commitHash
        );
        process.waitFor();

        // create input stream to get the output of the shell command
        InputStream inputStream = process.getInputStream();
        InputStreamReader inputStreamReader = new InputStreamReader(inputStream);
        return new BufferedReader(inputStreamReader);
    }
}
