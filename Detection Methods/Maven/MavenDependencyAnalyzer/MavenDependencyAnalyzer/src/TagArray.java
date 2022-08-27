import java.util.ArrayList;

/**
 * Class that contains useful functions for an array of Tags.
 */
public class TagArray {
    /**
     * Convert an array of Tags to a String representation.
     * @param arr array of Tags
     * @param description description of the TagArray
     * @param indent indentation used for printing
     * @return String representation of the TagArray
     */
    public static String toString(ArrayList<Tag> arr, String description, int indent) {
        StringBuilder stringBuilder = new StringBuilder();
        if (arr.size() > 0) {
            stringBuilder.append(description);
            for (Tag t : arr) {
                stringBuilder.append(t.toString(indent));
            }
        }
        return stringBuilder.toString();
    }

    /**
     * Compare two sorted arrays of Tags. The result of the comparison will
     * be printed.
     *
     * @param newTags first array of Tags
     * @param oldTags second array of Tags
     * @param diffAmounts amount of differences between two TagArrays
     * @param diff differences between two TagArrays
     */
    public static void compare(ArrayList<Tag> newTags, ArrayList<Tag> oldTags, StringBuilder diffAmounts, StringBuilder diff) {
        // arrays to store changed Tags
        ArrayList<Tag> added = new ArrayList<>();
        ArrayList<Tag> removed = new ArrayList<>();
        ArrayList<Tag> updated = new ArrayList<>();

        int iterNewTags = 0;
        int iterOldTags = 0;

        while (iterNewTags < newTags.size() && iterOldTags < oldTags.size()) {
            int difference = Tag.partialCompare(newTags.get(iterNewTags), oldTags.get(iterOldTags));

            if (difference == 0) {
                // check for update
                if (Tag.checkForUpdate(newTags.get(iterNewTags), oldTags.get(iterOldTags)) != 0) {
                    updated.add(newTags.get(iterNewTags));
                    updated.add(oldTags.get(iterOldTags));
                }
                ++iterNewTags;
                ++iterOldTags;
            } else if (difference < 0) {
                // new tag found
                added.add(newTags.get(iterNewTags));
                ++iterNewTags;
            } else {
                // tag removed
                removed.add(oldTags.get(iterOldTags));
                ++iterOldTags;
            }
        }

        for (; iterNewTags < newTags.size(); ++iterNewTags) {
            added.add(newTags.get(iterNewTags));
        }

        for (; iterOldTags < oldTags.size(); ++iterOldTags) {
            removed.add(oldTags.get(iterOldTags));
        }

        // produce result as StringBuilders
        diffAmounts.append(added.size()).append(", ").append(removed.size()).append(", ").append(updated.size() / 2).append(",\n");
        diff.append(toString(added, "    added: " + added.size() + "\n", 8))
                .append(toString(removed, "    removed: " + removed.size() + "\n", 8))
                .append(toString(updated, "    updated: " + updated.size() / 2 + "\n", 8));
    }
}
