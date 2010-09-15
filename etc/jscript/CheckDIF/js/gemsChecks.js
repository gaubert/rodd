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
//http://omasif.eumetsat.org/GEMS/HistoryFilterController.jsp?startTime=10.237&severity=A&endTime=10.238.00.00&severity=W&facility=DVB_KUBAND&host=&process=&search=%5E%28%28%3F%21eumcr04%29.%29*%24&regExp=1&pageSize=999&x=58&y=10
//TS START

function create_facilities_string(facilities) {

  // apply regular expression
  f_arr = facilities.split(/[\s,]+/)

  var result = "";
  for (var i = 0; i < f_arr .length; i++)
  {
     // to stay compatible gems_getLink_Check
     if (i == 0)
	 {
	    result = f_arr[i]; 
	 }
	 else
	 {
        //do stuff with str_arr [i]
	    result += "&facility="+f_arr[i];
     }
  }

  return result;

}

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
 * @param     integer mToGoBack  optional minutess in the past for start time
 * @param     integer mEToGoBack optional minutess in the past for end time
 * @param     integer mm         optional minutes of end time
 * @param     integer hh         optional hour of end time
 * @param     string  msg        optional the hyperlink text
 * @param     string  pre        optional a prefix to the the hyperlink
 * @param     string  post       optional a postfix to the the hyperlink
 * @param     string  id         optional tag id that will be used with jquery
 * @param     string  facilities optional list of facilities to search
 * @copyright &copy; 2006, {@link http://www.eumetsat.int}, 64295 Darmstadt
 * @package   Knowledge Base
 * @uses      UTCTimeString
 */
function gems_writeLink_Check_Morning_DIF(mToGoBack, mEToGoBack, mm, hh, msg, pre, post, id, facilities) {
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

	if (id == undefined) {
	   id = 'result'
	}

    if (facilities== undefined) 
	{ 
	   facilities = 'EPS_EXGATE&facility=EPS_COMMS&facility=EPS_DIF_G1&facility=EPS_DIF_COMMON&facility=EPS_GFT_CS';    } 
	else 
	{ 
	  facilities = create_facilities_string(facilities); 
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

	var href = gems_getLink_Check(strStart, strEnd, 'A&severity=W', facilities,  '', '', '', 999);
	return pre + '<a id="'+id+'" href="' + href + '">' + msg + '</a>' + strHint + strHint2 +  post;

}

/**
 * gems_getURL_Check_Morning_DIF
 *
 * This function creates a URL to check Common Facility Alarm events for daily reporting.
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
 * @param     integer mToGoBack  optional minutess in the past for start time
 * @param     integer mEToGoBack optional minutess in the past for end time
 * @param     integer mm         optional minutes of end time
 * @param     integer hh         optional hour of end time
 * @param     string  msg        optional the hyperlink text
 * @param     string  id         optional tag id that will be used with jquery
 * @param     string  facilities optional list of facilities to search
 * @package   Knowledge Base
 * @uses      UTCTimeString
 */
function gems_getURL_Check_Morning_DIF(mToGoBack, mEToGoBack, mm, hh, msg, id, facilities) {
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

	if (id == undefined) {
	   id = 'result'
	}

    if (facilities== undefined || facilities == '') 
	{ 
	   facilities = 'EPS_EXGATE&facility=EPS_COMMS&facility=EPS_DIF_G1&facility=EPS_DIF_COMMON&facility=EPS_GFT_CS';    } 
	else 
	{ 
	  facilities = create_facilities_string(facilities); 
	}

	var end   = new UTCTimeString(now);
	var start = new UTCTimeString(now - mToGoBack * 60000);
	var strStart = start.adoyhhmm;
	var strEnd   = end.adoyhhmm;

	var href = gems_getLink_Check(strStart, strEnd, 'A&severity=W', facilities,  '', '', '', 999);
	return href;

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
