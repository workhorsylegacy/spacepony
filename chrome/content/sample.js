
/*
see here for how to use:
https://developer.mozilla.org/en/Building_an_Extension
*/
var dbusnotify = {
	onLoad: function() {
		// initialization code
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
			} catch (e) {
				alert("error finding dbusnotify.py: " + error);
				return;
			}
			path += "/extensions/spacepony@workhorsy.org/chrome/content/dbusnotify.py";

			// Load the python script into an exec
			var exec = Components.classes["@mozilla.org/file/local;1"].createInstance(Components.interfaces.nsILocalFile);
			exec.initWithPath(path);

			// If it failed, show an error
			if(exec.exists()) {
				
			} else {
				alert("Error running dbusnotify.py");
				return;
			}

			// Run the exec in a process
			var process = Components.classes["@mozilla.org/process/util;1"].createInstance(Components.interfaces.nsIProcess);
			var args = ["Download Complete", aDownload.targetFile.path];
			process.init(exec);
			var exitvalue = process.run(true, args, args.length);
		} catch (e) {
			alert("DBus Notification Failed" + e);
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

