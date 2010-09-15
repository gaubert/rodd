/**
 * Class UTCTimeString
 *
 * This class provides some strings to be used for functions that need
 * UTC timestamps with the DOY = day of the year.
 *
 * Object properties:
 * .a          string year, four digits
 * .m          string month, two digits, with leading 0
 * .d          string date, two digits, with leading 0
 * .hh         string hours, two digits, with leading 0
 * .mm         string minutes, two digits, with leading 0
 * .ss         string seconds, two digits, with leading 0
 * .doy        string day of year, three digits, with leading 0
 * .adoyhhmmss string year.day_of_year.hours.minutes.seconds
 * .adoyhhmm   string year.day_of_year.hours.minutes
 *
 * USAGE example:
 *  var today = new UTCTimeString(); // implicit usage of actual time
 *	document.writeln('Today is the ' + start.doy + '. day of the year.');
 *
 *	var now   = new Date();
 *  var start = new UTCTimeString(now + 2 * 3600000); // two hours in the future
 *	document.writeln('The event starts in two hours at ' + start.adoyhhmm);
 *
 * @param     integer timestamp e.g. from timestamp=new Date();
 *
 * @author    Andreas Tusche <andreas.tusche@eumetsat.int>
 * @copyright &copy; 2006, {@link http://www.eumetsat.int}, 64295 Darmstadt
 * @package   Knowledge Base
 * @version   $Id: . Exp $;
 */
function UTCTimeString(timestamp) {
	var daysPerMonth = new Array( 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365);
	var now = new Date();

	if (timestamp != undefined) {
		now.setTime(timestamp);
	}

	/* UTC time */
	var utcFullYear  = now.getUTCFullYear();
	var utcMonth     = now.getUTCMonth(); /* Jan = 0, Feb = 1, ... */
	var utcDate      = now.getUTCDate();
	var utcHours     = now.getUTCHours();
	var utcMinutes   = now.getUTCMinutes();
	var utcSeconds   = now.getUTCSeconds();
	var utcDayOfYear = daysPerMonth[utcMonth] + utcDate;
	if (utcFullYear % 4 == 0 && utcMonth > 2) {
		if (utcFullYear % 100 != 0 || utcFullYear % 400 == 0) {
		  utcDayOfYear++;
		}
	}

	this.a          = utcFullYear.toString().substr(2, 2);
	this.m          = ((utcMonth     < 10)  ? '0' : '') + utcMonth;
	this.d          = ((utcDate      < 10)  ? '0' : '') + utcDate;
	this.hh         = ((utcHours     < 10)  ? '0' : '') + utcHours;
	this.mm         = ((utcMinutes   < 10)  ? '0' : '') + utcMinutes;
	this.ss         = ((utcSeconds   < 10)  ? '0' : '') + utcSeconds;
	this.doy        = ((utcDayOfYear < 100) ? '0' : '') + ((utcDayOfYear < 10) ? '0' : '') + utcDayOfYear;
	this.adoyhhmm   = this.a + '.' + this.doy + '.' + this.hh + '.' + this.mm;
	this.adoyhhmmss = this.adoyhhmm + '.' + this.ss;
} // end of class UTCTimeString

/* -- */
