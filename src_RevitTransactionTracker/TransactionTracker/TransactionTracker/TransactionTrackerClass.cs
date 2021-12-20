using System;
using System.IO;
using System.Diagnostics;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Events;
using Autodesk.Revit.UI;

namespace TransactionTracker
{
    //[Transaction(TransactionMode.Manual)]
    //[Regeneration(RegenerationOption.Manual)]
    public class TransactionTrackerClass : IExternalApplication
    {     
        public Result OnStartup(UIControlledApplication application)
        {
            try
            {
                // Register event. 
                application.ControlledApplication.DocumentOpened += application_DocumentOpened;
            }
            catch (Exception)
            {
                Console.WriteLine("Something went wrong during the registration process. ");
                Debug.WriteLine("Something went wrong during the registration process. ");
                return Result.Failed;
            }
            return Result.Succeeded;
        }

        public Result OnShutdown(UIControlledApplication application)
        {
            // remove the event.
            application.ControlledApplication.DocumentOpened -= application_DocumentOpened;
            return Result.Succeeded;
        }


        public void application_DocumentOpened(object sender, DocumentOpenedEventArgs args)
        {
            // get document from event args.
            Document doc = args.Document;

            var currentTime = DateTime.Now.ToFileTimeUtc().ToString();
            string loggingPath = @"C:\Users\ga38hep\dev\logging.txt";
            File.AppendAllText(loggingPath, currentTime + "TEST \n");
        }


    }
}
