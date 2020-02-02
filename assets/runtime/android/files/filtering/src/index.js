module.exports = {
  listClass: function() {
  var list = new java.util.List(String);
return "List created!";
  },


  arrayListClass: function() {
   var list = new java.util.ArrayList();
        return "Array List created!";
  },


  dateClass: function() {
    var list = new java.util.Date();
        return "Date created!";
  },


  timerClass: function() {
     var list = new java.util.Timer();
        return "Timer created!";
  },


    CFNumberCreate: function() {
     CFNumberCreate(null, null, null);
        return "CFNumberCreate created!";
  },

    CFArrayCreate: function() {
     CFArrayCreate(null,null,null,null);
        return "CFArrayCreate created!";
  },

    CFUUIDCreate: function() {
     CFUUIDCreate(null);
        return "CFUUIDCreate created!";
  },

    CFCalendarCopyCurrent: function() {
     var list = CFCalendarCopyCurrent();
        return "CFCalendarCopyCurrent created!";
  }
  }
