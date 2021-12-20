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

                application.ControlledApplication.DocumentCreated +=
                    new EventHandler<DocumentCreatedEventArgs>(document_created);

                application.ControlledApplication.DocumentChanged +=
                    new EventHandler<DocumentChangedEventArgs>(document_changed);


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

        /// <summary>
        /// Event method observing changes made to a Revit document
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        /// <exception cref="NotImplementedException"></exception>
        private void document_changed(object sender, DocumentChangedEventArgs e)
        {
            var transactionNames = e.GetTransactionNames();
            
            var addedElementIds = e.GetAddedElementIds();
            var deletedElementIds = e.GetDeletedElementIds();
            var modifiedElementIds = e.GetModifiedElementIds();

            // sometimes, transactions might happen without affecting elements but global settings.
            // Therefore, check beforehand if the event contains interesting knowledge. 
            if (addedElementIds == null && deletedElementIds == null && modifiedElementIds == null)
            {
                return;
            }

            var doc = e.GetDocument();

            foreach (var id in addedElementIds)
            {

                var ifcGuid = doc.GetElement(id).get_Parameter(BuiltInParameter.IFC_GUID);
                if (ifcGuid != null)
                {
                    Debug.WriteLine("[Transaction Tracker] - ADDED: " + ifcGuid.AsString());
                }
                else
                {
                    Debug.WriteLine("[Transaction Tracker] - ADDED: NoGUID" + " ElementId: " + id);
                }
            }

            foreach (var id in deletedElementIds)
            {
                var ifcGuid = doc.GetElement(id).get_Parameter(BuiltInParameter.IFC_GUID);
                if (ifcGuid != null)
                {
                    Debug.WriteLine("[Transaction Tracker] - DELETED: " + ifcGuid.AsString());
                }
                else
                {
                    Debug.WriteLine("[Transaction Tracker] - DELETED: NoGUID");
                }
            }

            foreach (var id in modifiedElementIds)
            {
                var ifcGuid = doc.GetElement(id).get_Parameter(BuiltInParameter.IFC_GUID);
                if (ifcGuid != null)
                {
                    Debug.WriteLine("[Transaction Tracker] - MODIFIED: IfcGUID:" + ifcGuid.AsString() + " ElementId: " + id);
                }
                else
                {
                    Debug.WriteLine("[Transaction Tracker] - MODIFIED: IfcGUID: NoGUID" + " ElementId: " + id);
                }
            }

        }

        private void document_created(object sender, DocumentCreatedEventArgs e)
        {
            throw new NotImplementedException();
        }

        #endregion
    }
}