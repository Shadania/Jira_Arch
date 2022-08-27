import java.io.File;
import java.io.IOException;
import java.util.Objects;

/**
 * Class that performs operations on directories.
 */
public class Directory {
    /**
     * Create a Git directory, e.g. a directory with the content of a Git commit.
     * @param directory directory used to store the content of the Git commit
     */
    public static void createGitDirectory(File directory) throws IOException, InterruptedException {
        directory.mkdirs();
        Git.clone(directory);
    }

    /**
     * Delete a directory and all its content (files and subdirectories).
     * @param currentDirectory directory to be deleted
     */
    public static void deleteDirectory(File currentDirectory) {
        File[] fileList = currentDirectory.listFiles();

        if (fileList == null) {
            return;
        }

        for (File file: fileList) {
            if (file.isDirectory()) {
                // delete subdirectory and its content
                deleteDirectory(file);
            } else {
                // delete file
                file.delete();
            }
        }
        // delete directory
        currentDirectory.delete();
    }
}
