
/*
See here for how to use:
https://developer.mozilla.org/en/Building_an_Extension

When developing, link to the extensions dir
ln -s ~/Desktop/sample/ ~/.mozilla/firefox/uryzgmqw.dev/extensions/spacepony@workhorsy.org
*/

var Helper = {
	RunProcess: function(is_blocking, process_path, args) {
		try {
			// Get the path of the script
			const DIR_SERVICE = new Components.Constructor("@mozilla.org/file/directory_service;1", "nsIProperties");
			var path = (new DIR_SERVICE()).get("ProfD", Components.interfaces.nsIFile).path;
			path += process_path;

			// https://developer.mozilla.org/En/Code_snippets/Running_applications
			// create an nsILocalFile for the executable
			var file = Components.classes["@mozilla.org/file/local;1"]
			            .createInstance(Components.interfaces.nsILocalFile);
			file.initWithPath(path);

			// If it failed, show an error
			if(!file.exists()) {
				throw("File to run not found: " + process_path);
			}

			// Create and run the process
			var process = Components.classes["@mozilla.org/process/util;1"]
			                .createInstance(Components.interfaces.nsIProcess);
			process.init(file);
			process.run(is_blocking, args, args.length);
		} catch(exception) {
			throw("Running process failed: " + String(exception));
		}
	}
}

// Bookmark Syncer
// https://developer.mozilla.org/en/Code_snippets/Bookmarks
var BookmarkManager = {
	onBeginUpdateBatch: function() {},
	onEndUpdateBatch: function() {},

	onItemAdded: function(aItemId, aFolder, aIndex) {
		// https://developer.mozilla.org/en/nsINavBookmarksService
		var bmsvc = Components.classes["@mozilla.org/browser/nav-bookmarks-service;1"]
		                    .getService(Components.interfaces.nsINavBookmarksService);
		var title = bmsvc.getItemTitle(aItemId);
		var guid = bmsvc.getItemGUID(aItemId);
		var uri = bmsvc.getBookmarkURI(aItemId).spec;
		var folder = "blah/blah/"; // FIXME: Find the real folder

		// Send a dbus event to the server
		Helper.RunProcess(
		true, 
		"/extensions/spacepony@workhorsy.org/chrome/content/fire_bookmark_added.py", 
		[folder, guid, title, uri]);
	},

	onItemRemoved: function(aItemId, aFolder, aIndex) {
		var bmsvc = Components.classes["@mozilla.org/browser/nav-bookmarks-service;1"]
		                    .getService(Components.interfaces.nsINavBookmarksService);
		var guid = bmsvc.getItemGUID(aItemId);

		// Send a dbus event to the server
		Helper.RunProcess(
		true, 
		"/extensions/spacepony@workhorsy.org/chrome/content/fire_bookmark_removed.py", 
		[guid]);
	},

	onItemChanged: function(aBookmarkId, aProperty, aIsAnnotationProperty, aValue) {
		var bmsvc = Components.classes["@mozilla.org/browser/nav-bookmarks-service;1"]
		                    .getService(Components.interfaces.nsINavBookmarksService);
		var guid = bmsvc.getItemGUID(aBookmarkId);
		var property_name = aProperty;
		var property_value = aValue;

		// Send a dbus event to the server
		Helper.RunProcess(
		true, 
		"/extensions/spacepony@workhorsy.org/chrome/content/fire_bookmark_changed.py", 
		[guid, property_name, property_value]);
	},

	onItemVisited: function(aBookmarkId, aVisitID, time) {},
	onItemMoved: function(aItemId, aOldParent, aOldIndex, aNewParent, aNewIndex) {},
	QueryInterface: XPCOMUtils.generateQI([Components.interfaces.nsINavBookmarkObserver]), 

	StartListening: function() {
		var bmsvc = Components.classes["@mozilla.org/browser/nav-bookmarks-service;1"]
				   .getService(Components.interfaces.nsINavBookmarksService);
		bmsvc.addObserver(BookmarkManager, false);
	}, 

	StoptListening: function() {
		var bmsvc = Components.classes["@mozilla.org/browser/nav-bookmarks-service;1"]
				   .getService(Components.interfaces.nsINavBookmarksService);
		bmsvc.addObserver(BookmarkManager, false);
	}, 

	InitialSync: function() {
		//alert("InitialSync");
/*
		var bmsvc = Components.classes["@mozilla.org/browser/nav-bookmarks-service;1"]
		                    .getService(Components.interfaces.nsINavBookmarksService);
		var ios = Components.classes["@mozilla.org/network/io-service;1"]
		                    .getService(Components.interfaces.nsIIOService);
		var menuFolder = bmsvc.bookmarksMenuFolder; // Bookmarks menu folder
		var newFolderId = bmsvc.createFolder(menuFolder, "pies of mud", bmsvc.DEFAULT_INDEX);
		var uri = ios.newURI("http://google.com/", null, null);
		var newBkmkId = bmsvc.insertBookmark(newFolderId, uri, bmsvc.DEFAULT_INDEX, "google");
*/
	}, 
};

var DownloadManager = {
	StartListening: function() {
		// Tell the download manager to send events to the DownloadManager
		this.dlMgr = Components.classes["@mozilla.org/download-manager;1"]
						.getService(Components.interfaces.nsIDownloadManager);
		this.dlMgr.addListener(DownloadManager);
	},

	SendNotification: function(aDownload) {
		// Send a dbus event to the server
		Helper.RunProcess(
		true, 
		"/extensions/spacepony@workhorsy.org/chrome/content/fire_download_complete.py", 
		["Download Complete", aDownload.targetFile.path]);
	},

	onDownloadStateChange: function(aState, aDownload) {
		switch(aDownload.state) {
			case Components.interfaces.nsIDownloadManager.DOWNLOAD_DOWNLOADING:
			case Components.interfaces.nsIDownloadManager.DOWNLOAD_FAILED:
			case Components.interfaces.nsIDownloadManager.DOWNLOAD_CANCELED:
				break;
			case Components.interfaces.nsIDownloadManager.DOWNLOAD_FINISHED:
				this.SendNotification(aDownload);
				break;
		}
	},

};

var Program = {
	onLoad: function() {
		//this.strings = document.getElementById("strings");

		// https://developer.mozilla.org/en/Retrieving_part_of_the_bookmarks_tree
		var historyService = Components.classes["@mozilla.org/browser/nav-history-service;1"]
		                               .getService(Components.interfaces.nsINavHistoryService);
		var options = historyService.getNewQueryOptions();
		var query = historyService.getNewQuery();

		var bookmarksService = Components.classes["@mozilla.org/browser/nav-bookmarks-service;1"]
		                                 .getService(Components.interfaces.nsINavBookmarksService);
		var toolbarFolder = bookmarksService.toolbarFolder;
		query.setFolders([toolbarFolder], 1);
		var result = historyService.executeQuery(query, options);

		// Look at all the bookmarks
		var unprocessed_nodes = [result.root];

		while(unprocessed_nodes.length > 0) {
			// https://developer.mozilla.org/en/nsINavHistoryResultNode
			var node = unprocessed_nodes.pop();

			// Normal bookmark
			if(node.type == Ci.nsINavHistoryResultNode.RESULT_TYPE_URI) {
				var title = node.title;
				var guid = ""; //node.guid; // FIXME: Find the real guid
				var uri = node.uri;
				var folder = "";

				// Get the complete folder path
				var parent = node.parent;
				while(parent != null) {
					folder = parent.title + "/" + folder;
					parent = parent.parent;
				}
				folder = "/" + folder;

				// Send a dbus event to the server
				Helper.RunProcess(
				true, 
				"/extensions/spacepony@workhorsy.org/chrome/content/fire_bookmark_added.py", 
				[folder, guid, title, uri]);
			// Folder
			} else if(node.type == Ci.nsINavHistoryResultNode.RESULT_TYPE_FOLDER) {
				node.QueryInterface(Ci.nsINavHistoryContainerResultNode);
				node.containerOpen = true;
				for(var i=0; i<node.childCount; i++) {
					unprocessed_nodes.push(node.getChild(i));
				}
				node.containerOpen = false;
			}
		}

		// Start listening to downloads
		DownloadManager.StartListening();

		// Sync the bookmarks, and continue listening for changes
		BookmarkManager.InitialSync();
		BookmarkManager.StartListening();
	}, 
}

window.addEventListener("load", function(e) { Program.onLoad(e); }, false);

