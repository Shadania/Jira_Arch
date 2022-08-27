import java.io.File;
import java.io.IOException;

/**
 * Class that performs Git commands using shell commands.
 */
public class Git {
    /**
     * Checkout a given Git commit.
     * @param commit hash of the commit to checkout
     * @param directory directory of the Git repository
     */
    public static void checkout(String commit, String directory) throws IOException, InterruptedException {
        Process process = Runtime.getRuntime().exec(
                Arguments.getGitProgramLocation() + " -C \"" + directory + "\" checkout " + commit
        );
        process.waitFor();
    }

    /**
     * Clone a given Git repository.
     * @param directory directory to run the Git command
     */
    public static void clone(File directory) throws IOException, InterruptedException {
        Process process = Runtime.getRuntime().exec(
                Arguments.getGitProgramLocation() + " -C " + directory + " clone " + Arguments.getRepositoryUrl()
        );
        process.waitFor();
    }
}
