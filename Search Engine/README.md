This Search Engine works off of the (manually or otherwise) classified issues. They are inserted into the search engine in ways documented below and through the frontend can be indexed and searched to find specific knowledge.

# How to run
First, start the backend. Then, run the frontend. Now, you should be able to access the frontend on `localhost:420`. More detailed instructions for back- and frontend in the respective folders.


# How to use the Search Engine

## Old Usage Guides
Note that accessing these documents may require you to request permission. Additionally, they may not be entirely up to date anymore.

- [Steps to set up the environment](https://docs.google.com/document/d/1RJhU2w3XLODsNbTUNbwatcU6dYBrHAZGCRLndjJI-4k/edit)
- [Site User Guide](https://docs.google.com/document/d/1DYtzWahtR1CmjO6pBcleQ0aQKj4qGfu0OXq4KosSuV4/edit)

## Adding new Issues to the Database
This needs to be done through the frontend, in order to format the correct query for the backend. Do not insert issue data directly into the database without also adding the equivalent indices, or the index will not be correct.

Things to do with the index go through the 'Reindex' tab. On this page, you have several options: to reindex the entire database, reindex only certain IDs, or upload a classification document. This document is expected to be a .csv with at least the following headers: 'issue_id', 'Existence', 'Property', and 'Executive'. These are not case sensitive, but the underscore in issue_id is required. Additionally, if you want a particular tag to accompany these issues specifically, you can fill it in in the second field.

Please note that if your classification is significantly newer, you will have to first check for new issues in the issue list. The classification upload cannot add tags to issues it does not yet know. You can refresh an issue list by finding it in the 'Manage/Issue List' tab and pressing 'Get new issues'. If you do not do this, there will be errors in the backend, and the classification may be only partially uploaded. In the future, the frontend should be able to tell the user that this has happened.

## Define Scope of Issues to Search
In order to search issues, we need to know what to search. A Query Collection can contain multiple issue lists and mailing lists, but since mailing lists do not currently work, this example will stick to Issue Lists.

Under Manage, in the tab Issue List, click the green Add Issue List button. Fill in the name with something you will recognize, and fill in the key for the appropriate Jira issues, e.g. for Cassandra, all Cassandra issue keys start with CASSANDRA, so for that project, the key is CASSANDRA.

After adding all the issue lists you want, go to Query Collection and create one by filling in a name and ticking the boxes of the issue lists you want in this query collection.

In order to just search issues, you likely do not need to add any tags yourself: these should already be there thanks to the index.

Now that you have your query collection set up, go back to the Home page and select your newly made collection from the list. Now, at the top of the page, you can search for issues, and on the left, you can isolate a certain issue list. Happy searching!

## Search Query Formatting
The query collection's search bar works with Apache Lucene formatting. 

The available fields to search are:

- 'id': the integer ID from the database
- 'key': the Jira issue key
- 'tag': an issue can have multiple of these or none, based on which tags it has
- 'summary': the title of an issue
- 'description': the description of an issue
- 'comments': the collective text of all comments on this issue

A few examples below:
```
key:"CASSANDRA-6311"
```
Finds all issues which have CASSANDRA-6311 as key. There should only be one such issue.

```
tag:"MAVEN" AND tag:"Existence"
```
Find all issues which have the MAVEN *and* Existence tags.

```
tag:"MAVEN" AND (tag:"Existence" OR tag:"Property") AND NOT tag:"Executive"
```
Find all issues that were tagged MAVEN *and* Existence or Property, but not Executive.

```
key:"TAJO-*" AND tag:"MAVEN"
```
Finds all issues with keys that start with TAJO- and which are tagged with the MAVEN tag.

Find Lucene search query parser syntax documentation [here](https://lucene.apache.org/core/2_9_4/queryparsersyntax.html).