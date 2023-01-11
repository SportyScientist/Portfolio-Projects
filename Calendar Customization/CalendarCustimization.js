function ColorEvents() {

    var today = new Date();
    var nextweek = new Date();
    nextweek.setDate(nextweek.getDate() + 7);
    Logger.log(today + " " + nextweek);
  
    var calendars = CalendarApp.getAllOwnedCalendars();
    Logger.log("found number of calendars: " + calendars.length);
  
    for (var i=0; i<calendars.length; i++) {
      var calendar = calendars[i];
      var events = calendar.getEvents(today, nextweek);
      var sports = ['crossfit'];
      var works = ['work'];
      var met = ['meeting'];
      var nachhilfe = ['biologie-', 'chemie-'];
      var music = ['klavier'];
   
      for (var j=0; j<events.length; j++) {
        var e = events[j];
        var title1 = e.getTitle();
        var title = title1.toLowerCase()
  
        
        var foundsports = sports.some(el => title.includes(el));
        var foundwork = works.some(el => title.includes(el));
        var foundmet = met.some(el => title.includes(el));
        var foundhilfe = nachhilfe.some(el => title.includes(el));
        var foundmusic = music.some(el => title.includes(el));
  
         
        if (foundwork === true) {
          e.setColor(CalendarApp.EventColor.ORANGE);
        }
        if (foundsports === true) {
          e.setColor(CalendarApp.EventColor.YELLOW);
        }     
        if (foundmet === true) {
          e.setColor(CalendarApp.EventColor.GREEN);
        } 
        if (foundhilfe === true) {
          e.setColor(CalendarApp.EventColor.PALE_GREEN);
        } 
         if (foundmusic === true) {
          e.setColor(CalendarApp.EventColor.GRAY);
        } 
      }
    }
  }
  