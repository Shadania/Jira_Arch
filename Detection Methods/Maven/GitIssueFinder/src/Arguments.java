/**
 * Class to store the arguments that were given to the program and
 * the variables that are used globally.
 */
public class Arguments {
    private static String GIT_PROGRAM_LOCATION = "";
    private static String GIT_REPOSITORY_LOCATION = "";
    private static String[] ISSUE_PREFIXES;
    private static String OUTPUT_FILE = "";

    public static String getGitProgramLocation() {
        return GIT_PROGRAM_LOCATION;
    }

    public static void setGitProgramLocation(String gitProgramLocation) {
        GIT_PROGRAM_LOCATION = gitProgramLocation;
    }

    public static String getGitRepositoryLocation() {
        return GIT_REPOSITORY_LOCATION;
    }

    public static void setGitRepositoryLocation(String gitRepositoryLocation) {
        GIT_REPOSITORY_LOCATION = gitRepositoryLocation;
    }

    public static String[] getIssuePrefixes() {
        return ISSUE_PREFIXES;
    }

    public static void setIssuePrefixes(String issuePrefixes) {
        ISSUE_PREFIXES = issuePrefixes.split(",");
    }

    public static String getOutputFile() {
        return OUTPUT_FILE;
    }

    public static void setOutputFile(String outputFile) {
        OUTPUT_FILE = outputFile;
    }
}
