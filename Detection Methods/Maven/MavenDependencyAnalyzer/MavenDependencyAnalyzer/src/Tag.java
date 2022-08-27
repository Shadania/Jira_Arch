import java.util.ArrayList;

/**
 * Class to implement Tags. Tags represent the dependencies and its exclusions that
 * can be found in POM files.
 */
public class Tag {
    private String tagName;
    private String file;
    private String artifactPomId;
    private String artifactId;
    private String groupId;
    private String version;
    private ArrayList<Tag> exclusions;

    public Tag() {
        tagName = "";
        artifactId = "";
        groupId = "";
        version = "";
        file = "";
        artifactPomId = "";
        exclusions = new ArrayList<>();
    }

    public void setTagName(String tagName) {
        this.tagName = tagName;
    }

    public void setFile(String file) {
        this.file = file;
    }

    public void setArtifactPomId(String artifactPomId) {
        this.artifactPomId = artifactPomId;
    }

    public void setArtifactId(String artifactId) {
        this.artifactId = artifactId;
    }

    public void setGroupId(String groupId) {
        this.groupId = groupId;
    }

    public String getGroupId() {
        return this.groupId;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    public String getVersion() {
        return this.version;
    }

    public void setExclusions(ArrayList<Tag> exclusions) {
        this.exclusions = exclusions;
    }

    /**
     * Check whether the file, artifactPomId, artifactId and groupId are the same
     * for the two given Tags. If they are the same, the function returns 0.
     * If they are not the same, the result of the comparison of the unequal
     * element will be returned.
     *
     * @param lhs first Tag
     * @param rhs second Tag
     * @return result of comparison (0 for equal Tags, else unequal Tags)
     */
    public static int partialCompare(Tag lhs, Tag rhs) {
        int result;

        // compare file
        if ((result = lhs.file.compareTo(rhs.file)) != 0) {
            return result;
        }

        // compare artifactPomId
        if ((result = lhs.artifactPomId.compareTo(rhs.artifactPomId)) != 0) {
            return result;
        }

        // compare artifactId
        if ((result = lhs.artifactId.compareTo(rhs.artifactId)) != 0) {
            return result;
        }

        // compare groupId
        return lhs.groupId.compareTo(rhs.groupId);
    }

    /**
     * Compares the exclusions of two tags.
     * @param lhs exclusions of the first tag
     * @param rhs exclusions of the second tag
     * @return comparison value (0 is equal, non 0 is not equal)
     */
    private static int compareExclusions(ArrayList<Tag> lhs, ArrayList<Tag> rhs) {
        // compare exclusion array sizes
        if (lhs.size() < rhs.size()) {
            return -1;
        }
        if (lhs.size() > rhs.size()) {
            return 1;
        }

        // compare the exclusions
        for (int iter = 0; iter < lhs.size(); ++iter) {
            int result;
            if ((result = Tag.compare(lhs.get(iter), rhs.get(iter))) != 0) {
                return result;
            }
        }

        // exclusions are the same
        return 0;
    }

    /**
     * Fully compare two Tags
     * @param lhs first Tag
     * @param rhs second Tag
     * @return value of comparison
     */
    public static int compare(Tag lhs, Tag rhs) {
        int result;

        // compare the first part of the Tags
        if ((result = partialCompare(lhs, rhs)) != 0) {
            return result;
        }

        // compare version
        if ((result = lhs.version.compareTo(rhs.version)) != 0) {
            return result;
        }

        // compare exclusions arrays
        return compareExclusions(lhs.exclusions, rhs.exclusions);
    }

    /**
     * Checks if a Tag is updated compared to another Tag.
     * @param lhs first Tag
     * @param rhs second Tag
     * @return comparison value (0 if not updated, else updated)
     */
    public static int checkForUpdate(Tag lhs, Tag rhs) {
        int result;

        // compare version
        if ((result = lhs.version.compareTo(rhs.version)) != 0) {
            return result;
        }

        // compare exclusions arrays
        return compareExclusions(lhs.exclusions, rhs.exclusions);
    }

    /**
     * Converts a Tag to a String representation.
     * @param indent indentation used for printing
     * @return String representation of the Tag
     */
    public String toString(int indent) {
        StringBuilder stringBuilder = new StringBuilder();

        // tagName begin to String
        stringBuilder.append(" ".repeat(indent)).append("<").append(this.tagName).append(">\n");

        // file to String
        if (!file.equals("")) {
            stringBuilder.append(" ".repeat(indent + 4)).append("file=").append(this.file).append("\n");
        }

        // artifactPomId to String
        if (!artifactPomId.equals("")) {
            stringBuilder.append(" ".repeat(indent + 4)).append("artifactPomId=").append(this.artifactPomId).append("\n");
        }

        // artifactId to String
        if (!artifactId.equals("")) {
            stringBuilder.append(" ".repeat(indent + 4)).append("artifactId=").append(this.artifactId).append("\n");
        }

        // groupId to String
        if (!groupId.equals("")) {
            stringBuilder.append(" ".repeat(indent + 4)).append("groupId=").append(this.groupId).append("\n");
        }

        // version to String
        if (!version.equals("")) {
            stringBuilder.append(" ".repeat(indent + 4)).append("version=").append(this.version).append("\n");
        }

        // exclusions to String
        for (Tag exclusion : this.exclusions) {
            stringBuilder.append(exclusion.toString(indent + 4));
        }

        // tagName end to String
        stringBuilder.append(" ".repeat(indent)).append("</").append(this.tagName).append(">\n");

        return stringBuilder.toString();
    }
}
