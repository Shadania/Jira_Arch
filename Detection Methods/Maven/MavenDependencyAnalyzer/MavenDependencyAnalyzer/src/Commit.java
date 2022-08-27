import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Objects;

/**
 * Class that converts the POM files in a Git commit to a TagArray.
 */
public class Commit {
    /**
     * Function that returns a remotely defined version, either defined as a Tag
     * on its own or a property.
     * @param name name of the remotely defined version
     * @param document document containing remote version
     * @return remote version
     */
    private static String getRemoteVersion(String name, Document document) {
        // remote version defined in its own node under <properties>
        NodeList nodes = document.getElementsByTagName(name);
        if (nodes.getLength() > 0) {
            return nodes.item(0).getTextContent();
        }

        // remote version defined as a <property>
        nodes = document.getElementsByTagName("property");
        for (int iter = 0; iter < nodes.getLength(); ++iter) {
            Node nameNode = nodes.item(iter).getAttributes().getNamedItem("name");
            Node valueNode = nodes.item(iter).getAttributes().getNamedItem("value");

            if (nameNode == null || valueNode == null) {
                // not a node with a remote version
                continue;
            }

            if (nameNode.getNodeValue().equals(name)) {
                // node containing the remote version
                return valueNode.getNodeValue();
            }
        }

        // no remote version found
        return name;
    }

    /**
     * Function that only returns a remote version if it is defined.
     * @param version version defined in a Tag
     * @param document document containing remote version
     * @return remote version if defined
     */
    private static String maybeGetRemoteVersion(String version, Document document) {
        if (version.length() == 0) {
            // empty version defined at all
            return version;
        }

        if (version.charAt(0) == '$') {
            // remote version defined
            return getRemoteVersion(version.substring(2, version.length() - 1), document);
        }

        // no remote version defined
        return version;
    }

    /**
     * Converts a Node to a Tag. The Tag is returned by the function.
     *
     * @param node          Node to be converted
     * @param tagName       tagName attribute for the Tag that will be returned
     * @param file          file attribute for the Tag that will be returned
     * @param artifactPomId artifactPomId attribute for the Tag that will be returned
     * @param document      document containing POM information
     * @return the Tag that was converted from the Node
     */
    private static Tag nodeToTag(Node node, String tagName, String file, String artifactPomId, Document document) {
        Tag tag = new Tag();

        // assign given information about the Tag to the Tag
        tag.setTagName(tagName);
        tag.setFile(file);
        tag.setArtifactPomId(artifactPomId);

        if (node.hasAttributes()) {
            // node has attributes that contain information
            for (int i = 0; i < node.getAttributes().getLength(); ++i) {
                switch (node.getAttributes().item(i).getNodeName()) {
                    case "artifactId" -> tag.setArtifactId(node.getAttributes().item(i).getNodeValue());
                    case "groupId" -> tag.setGroupId(node.getAttributes().item(i).getNodeValue());
                    case "version" -> tag.setVersion(node.getAttributes().item(i).getNodeValue());
                }
            }
        } else {
            // node has child nodes that contain information
            for (int i = 0; i < node.getChildNodes().getLength(); ++i) {
                switch (node.getChildNodes().item(i).getNodeName()) {
                    case "artifactId" -> tag.setArtifactId(node.getChildNodes().item(i).getTextContent());
                    case "groupId" -> tag.setGroupId(node.getChildNodes().item(i).getTextContent());
                    case "version" -> tag.setVersion(node.getChildNodes().item(i).getTextContent());
                }
            }
        }

        // get remotely defined version if available
        tag.setVersion(maybeGetRemoteVersion(tag.getVersion(), document));

        // add the exclusions to the dependency tag
        ArrayList<Tag> exclusions = new ArrayList<>();
        getTags("exclusion", node.getChildNodes(), exclusions, "", "", document);
        exclusions.sort(Tag::compare);
        tag.setExclusions(exclusions);

        return tag;
    }

    /**
     * Get all tags from a NodeList with the given tagName.
     *
     * @param tagName       tagName of the Tags that need to be found
     * @param nl            NodeList that contains the Tags
     * @param arr           array to store the found Tags
     * @param file          file attribute of the Tags that need to be found
     * @param artifactPomId artifactPomId of the Tags that need to be found
     * @param document      document containing POM information
     */
    private static void getTags(String tagName, NodeList nl, ArrayList<Tag> arr, String file, String artifactPomId, Document document) {
        // loop through the NodeList
        for (int i = 0; i < nl.getLength(); ++i) {
            if (nl.item(i).getNodeName().equals(tagName)) {
                // tag found with the correct tagName
                Tag tag = nodeToTag(nl.item(i), tagName, file, artifactPomId, document);

                // apply filter
                if (!tag.getGroupId().equals(Arguments.getFilter())) {
                    arr.add(tag);
                }
            } else {
                if (nl.item(i).getChildNodes() != null) {
                    // search for tags in the child nodes
                    getTags(tagName, nl.item(i).getChildNodes(), arr, file, artifactPomId, document);
                }
            }
        }
    }

    /**
     * Get all files with a given filename from a directory and its subdirectories.
     * @param filename filename of the files that need to be found
     * @param directory directory in which will be searched
     * @param files array to store the files found
     */
    private static void getFilesFromDirectory(String filename, File directory, ArrayList<File> files) {
        // loop through current directory
        for (File file : Objects.requireNonNull(directory.listFiles())) {
            if (file.isDirectory()) {
                // search in subdirectory
                getFilesFromDirectory(filename, file, files);
            } else {
                // check if the found file has the correct name
                if (file.getName().equals(filename)) {
                    // file has correct name
                    files.add(file);
                }
            }
        }
    }

    /**
     * Get all dependencies in the POM files of a commit as a TagArray
     * @param commit hash of the commit where the dependencies will be searched for
     * @param directory directory that contains the content of the commit
     * @return TagArray with the dependencies in the POM files of a commit
     */
    public static ArrayList<Tag> toTagArray(String commit, String directory) throws IOException, InterruptedException {
        // checkout commit
        Git.checkout(commit, directory);

        ArrayList<Tag> arr = new ArrayList<>();

        // get all files in the commit with a certain filename
        ArrayList<File> files = new ArrayList<>();
        getFilesFromDirectory(Arguments.getPomFileName(), new File(directory), files);

        // loop through the files that were found
        for (File file : files) {
            // convert the file to an XML document
            Document document;
            try {
                DocumentBuilderFactory documentBuilderFactory = DocumentBuilderFactory.newInstance();
                DocumentBuilder documentBuilder = documentBuilderFactory.newDocumentBuilder();
                document = documentBuilder.parse(file);
            } catch (SAXException | ParserConfigurationException exception) {
                System.err.println("[Error] analyzing commit: " + commit + " has failed");
                return null;
            }

            // find all elements named "artifact:pom"
            NodeList poms = document.getElementsByTagName("artifact:pom");

            // get tags from artifact:pom
            for (int idx = 0; idx < poms.getLength(); ++idx) {
                String artifactPomId = poms.item(idx).getAttributes().getNamedItem("id").getNodeValue();
                getTags("dependency", poms.item(idx).getChildNodes(), arr, file.getAbsolutePath(), artifactPomId, document);
            }

            // get tags directly by the tagName if artifact pom is not used
            if (poms.getLength() == 0) {
                poms = document.getElementsByTagName("dependency");
                for (int idx = 0; idx < poms.getLength(); ++idx) {
                    Tag tag = nodeToTag(poms.item(idx), "dependency", file.getAbsolutePath(), "", document);

                    // apply filter
                    if (!tag.getGroupId().equals(Arguments.getFilter())) {
                        arr.add(tag);
                    }
                }
            }
        }

        arr.sort(Tag::compare);

        return arr;
    }
}
