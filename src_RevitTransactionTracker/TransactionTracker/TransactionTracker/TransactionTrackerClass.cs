using System;
using System.IO;
using System.Diagnostics;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Events;
using Autodesk.Revit.UI;

namespace TransactionTracker
{
    public class TransactionTrackerClass : IExternalApplication
    {
        #region IExternalApplication

        public Result OnStartup(UIControlledApplication application)
        {
            //String version = application.ControlledApplication.VersionName;
            //Debug.WriteLine(version);

            try
            {
                // Register event. 
                //application.ControlledApplication.DocumentOpened += application_DocumentOpened;
                application.ControlledApplication.DocumentOpened +=
                    new EventHandler<Autodesk.Revit.DB.Events.DocumentOpenedEventArgs>(application_DocumentOpened);
                application.ControlledApplication.DocumentSaved +=
                    new EventHandler<Autodesk.Revit.DB.Events.DocumentSavedEventArgs>(application_DocumentSaved);
                Debug.WriteLine("[Transaction Tracker] Mounted Transaction tracker successfully. ");
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
            application.ControlledApplication.DocumentSaved -= application_DocumentSaved;

            Debug.WriteLine("[Transaction Tracker] Unmounted Transaction tracker successfully. ");
            return Result.Succeeded;
        }

        #endregion

        #region Event manager
        

        public void application_DocumentOpened(object sender, DocumentOpenedEventArgs args)
        {
            Debug.WriteLine("[Transaction Tracker] Triggered event listener");

            try
            {
                // get document from event args.
                Document doc = args.Document;

                var currentTime = DateTime.Now.ToFileTimeUtc().ToString();
                string loggingPath = @"C:\Users\ga38hep\dev\logging.txt";
                File.AppendAllText(loggingPath, currentTime + "TEST \n");
            }
            catch (Exception e)
            {
                Console.WriteLine(e);
                Debug.WriteLine(e);
            }
        }

        private void application_DocumentSaved(object sender, DocumentSavedEventArgs e)
        {
            Debug.WriteLine("[Transaction Tracker] Triggered event listener");
        }
        #endregion
    }
}