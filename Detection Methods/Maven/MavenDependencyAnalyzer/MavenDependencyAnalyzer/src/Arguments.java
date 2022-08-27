/**
 * Class to store the arguments that were given to the program. Each class
 * can get the arguments using the getters that are available.
 */
public class Arguments {
    private static String POM_FILE_NAME = "";
    private static String GIT_PROGRAM_LOCATION = "";
    private static String REPOSITORY_URL = "";
    private static String REPOSITORY_NAME = "";
    private static String FILTER = "";

    public static String getPomFileName() {
        return POM_FILE_NAME;
    }

    public static void setPomFileName(String pomFileName) {
        POM_FILE_NAME = pomFileName;
    }

    public static String getGitProgramLocation() {
        return GIT_PROGRAM_LOCATION;
    }

    public static void setGitProgramLocation(String programLocation) {
        GIT_PROGRAM_LOCATION = programLocation;
    }

    public static String getRepositoryUrl() {
        return REPOSITORY_URL;
    }

    public static void setRepositoryUrl(String repositoryUrl) {
        REPOSITORY_URL = repositoryUrl;
    }

    public static String getRepositoryName() {
        return REPOSITORY_NAME;
    }

    public static void setRepositoryName(String repositoryName) {
        REPOSITORY_NAME = repositoryName;
    }

    public static String getFilter() {
        return FILTER;
    }

    public static void setFilter(String filter) {
        Arguments.FILTER = filter;
    }
}
