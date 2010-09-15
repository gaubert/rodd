/**
 * @author    Andreas Tusche <andreas.tusche@eumetsat.int>
 * @copyright &copy; 2006, {@link http://www.eumetsat.int}, 64295 Darmstadt
 * @package   Knowledge Base
 * @todo      merge and or compact functions
 * @update    TS hacks to original ATu code.
 */

/**
 * function gems_getLinkCheck
 *
 * This function creates the URL for a hyperlink for the GEMS check.
 *
 * @param string startTime
 * @param string endTime
 * @param string severity
 * @param string facility
 * @param string host
 * @param string process
 * @param string search
 * @param string pageSize
 *
 * @author    Andreas Tusche <andreas.tusche@eumetsat.int>
 * @copyright &copy; 2006, {@link http://www.eumetsat.int}, 64295 Darmstadt
 * @package   Knowledge Base
 * @todo Update this link, when GEMS changes configuration
 */
function gems_getLink_Check(startTime, endTime, severity, facility, host, process, search, pageSize) {
	return 'http://omasif.eumetsat.org/GEMS/HistoryFilterController.jsp'
		+ '?startTime=' + startTime
		+ '&endTime='   + endTime
		+ '&severity='  + severity
		+ '&facility='  + facility
		+ '&host='      + host
		+ '&process='   + process
		+ '&search='    + search
		+ '&pageSize='  + pageSize
		+ '&x=1&y=1';
}


//TS START

/**
 * gems_writeLink_Check_Morning_DIF
 *
 * This function creates a hyperlink to check Common Facility Alarm events for daily reporting.
 * The time starts 2 hours before the actual system time on the local
 * computer and ends at the current time.
 *
 * If the optional parameters hh and mm are set, the returned hyperlink
 * is created for an end time today at the given hour (hh) and minute (mm).
 *
 * If the optional parameters pre and post are not set, the hyperlink
 * is embedded in a paragraph of CSS class '.linkCheckGEMS'.
 *
 * USAGE example:
 *   gems_writeLink_Check_CF_A()
 *   gems_writeLink_Check_CF_A( 1, 30, 6, 'RSS checks (last hour)', '<li>', '</li>');
 *
 * @param     integer hToGoBack  optional hours in the past for start time
 * @param     integer mm         optional minutes of end time
 * @param     integer hh         optional hour of end time
 * @param     string  msg        optional the hyperlink text
 * @param     string  pre        optional a prefix to the the hyperlink
 * @param     string  post       optional a postfix to the the hyperlink
 * @copyright &copy; 2006, {@link http://www.eumetsat.int}, 64295 Darmstadt
 * @package   Knowledge Base
 * @uses      UTCTimeString
 */
function gems_writeLink_Check_Morning_DIF(mToGoBack, mEToGoBack, mm, hh, msg, pre, post) {
	var now   = new Date();
	var strHint = '';
	var strHint2 = '';

	if (mToGoBack == undefined) {
		//now.setUTCMinutes(00);         // set to 00 minutes
		mToGoBack = 120;                 // start hours in the past
		strHint = ' ';
	}

	if (mEToGoBack == undefined) {
		//now.setUTCMinutes(00);         // set to 00 minutes
		mEToGoBack = 120;                 // start hours in the past
		strHint2 = ' ';
	}

	if (mm != undefined) {
		now.setUTCMinutes(mm);//15/04/2008 11:57
	}

	if (hh != undefined) {
		now.setUTCHours(hh);
	}

	if (pre == undefined) {
		pre = '<p class="linkCheckGEMS">';
	}

	if (post == undefined) {
		post = "</p>\n";
	}
	var end   = new UTCTimeString(now);
	var start = new UTCTimeString(now - mToGoBack * 60000);
	var strStart = start.adoyhhmm;
	var strEnd   = end.adoyhhmm;

		msg = msg + ' : ' + strStart + ' to ' + strEnd;

	if (msg == undefined) {
		msg = 'EPS DIF Morning Checks - Last 36 hours  ' + strStart + ' to ' + strEnd;
	}

	var href = gems_getLink_Check(strStart, strEnd, 'A&severity=W', 'EPS_EXGATE&facility=EPS_COMMS&facility=EPS_DIF_G1&facility=EPS_DIF_COMMON&facility=EPS_GFT_CS',  '', '', '', 999);
	document.write(pre + '<a href="' + href + '">' + msg + '</a>' + strHint + strHint2 +  post);
	return;
}


function write_time_now() {
	var now   = new Date();
	var time = new UTCTimeString(now);
	document.write('<p>' + 'Local time now is: ' + now + '</p>' + '<p>' + ' or ' + time.adoyhhmmss + ' UTC' + '</p>');
	return;
}

function mail_me() {
	var now   = new Date();
	var time = new UTCTimeString(now);
	var pre = '<a href="mailto:tom.sheasby@eumetsat.int?subject=Morning%20Checks&amp;body=';
	var post = '">Mail Me</a>';
	var messageBody = ('Email generated at: ' + now);
	document.write(pre + messageBody + post);
	return;
}


//TS END
/* -- */