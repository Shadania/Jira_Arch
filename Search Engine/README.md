This Search Engine works off of the (manually or otherwise) classified issues. They are inserted into the search engine in ways documented below and through the frontend can be indexed and searched to find specific knowledge.

# How to run
First, start the backend. Then, run the frontend. Now, you should be able to access the frontend on `localhost:420`. More detailed instructions for back- and frontend in the respective folders.


# How to use the Search Engine

## Old Usage Guides
Note that accessing these documents may require you to request permission. Additionally, they may not be entirely up to date anymore.

- https://docs.google.com/document/d/1RJhU2w3XLODsNbTUNbwatcU6dYBrHAZGCRLndjJI-4k/edit : "Steps to set up the environment"
- https://docs.google.com/document/d/1DYtzWahtR1CmjO6pBcleQ0aQKj4qGfu0OXq4KosSuV4/edit : "Site User Guide"

## Adding new Issues to the Database
This needs to be done through the frontend, in order to format the correct query for the backend. Do not insert issue data directly into the database without also adding the equivalent indices, or the index will not be correct.

(todo add instruction here)

## Searching Issues
In order to search issues, we need to know what to search. A Query Collection can contain multiple issue lists and mailing lists, but since mailing lists do not currently work, this example will stick to Issue Lists.

Under Manage, in the tab Issue List, click the green Add Issue List button. Fill in the name with something you will recognize, and fill in the key for the appropriate Jira issues, e.g. for Cassandra, all Cassandra issue keys start with CASSANDRA, so for that project, the key is CASSANDRA.

After adding all the issue lists you want, go to Query Collection and create one by filling in a name and ticking the boxes of the issue lists you want in this query collection.

In order to just search issues, you likely do not need to add any tags yourself: these should already be there thanks to the index.

Now that you have your query collection set up, go back to the Home page and select your newly made collection from the list. Now, at the top of the page, you can search for issues, and on the left, you can isolate a certain issue list. Happy searching!