
/*
See here for how to use:
https://developer.mozilla.org/en/Building_an_Extension

When developing, link to the extensions dir
ln -s ~/Desktop/sample/ ~/.mozilla/firefox/uryzgmqw.dev/extensions/spacepony@workhorsy.org
*/
var dbusnotify = {
	onLoad: function() {
		this.initialized = true;
		this.strings = document.getElementById("dbusnotify-strings");
	
		this.dlMgr = Components.classes["@mozilla.org/download-manager;1"]
						.getService(Components.interfaces.nsIDownloadManager);
		this.dlMgr.addListener(dbusnotify);
	},

	notify: function(aDownload) {
		try {
			// Get the path of the dbus script
			const DIR_SERVICE = new Components.Constructor("@mozilla.org/file/directory_service;1", "nsIProperties");
			var path = '';
			try {
				path = (new DIR_SERVICE()).get("ProfD", Components.interfaces.nsIFile).path;
			} catch(exception) {
				alert("error finding dbusnotify.py: " + exception);
				return;
			}
			path += "/extensions/spacepony@workhorsy.org/chrome/content/dbusnotify.py";

			// https://developer.mozilla.org/En/Code_snippets/Running_applications
			// create an nsILocalFile for the executable
			var file = Components.classes["@mozilla.org/file/local;1"]
						.createInstance(Components.interfaces.nsILocalFile);
			file.initWithPath(path);

			// If it failed, show an error
			if(!file.exists()) {
				alert("Error running dbusnotify.py");
				return;
			}

			// Create and run the process
			var process = Components.classes["@mozilla.org/process/util;1"]
							.createInstance(Components.interfaces.nsIProcess);
			var args = ["Download Complete", aDownload.targetFile.path];
			process.init(file);
			var exitvalue = process.run(true, args, args.length);
		} catch(exception) {
			alert("DBus Notification Failed" + exception);
			return;
		}
	},

	onDownloadStateChange: function(aState, aDownload) {
		switch(aDownload.state) {
			case Components.interfaces.nsIDownloadManager.DOWNLOAD_DOWNLOADING:
			case Components.interfaces.nsIDownloadManager.DOWNLOAD_FAILED:
			case Components.interfaces.nsIDownloadManager.DOWNLOAD_CANCELED:
				break;
			case Components.interfaces.nsIDownloadManager.DOWNLOAD_FINISHED:
				this.notify(aDownload);
				break;
		}
	},

};

window.addEventListener("load", function(e) { dbusnotify.onLoad(e); }, false);

