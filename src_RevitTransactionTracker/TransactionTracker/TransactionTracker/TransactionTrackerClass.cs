using System;
using System.Collections.Generic;
using System.IO;
using System.Diagnostics;
using System.Linq;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Analysis;
using Autodesk.Revit.DB.Events;
using Autodesk.Revit.UI;

namespace TransactionTracker
{
    public class TransactionTrackerClass : IExternalApplication
    {
        #region Properties

        readonly ServerConnector _connector = new ServerConnector();


        #endregion


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

            var names = transactionNames.Aggregate("", (current, name) => current + (name + ", "));
            Debug.WriteLine($"[Transaction Tracker] Transaction Names: {names}");

            // sometimes, transactions might happen without affecting elements but global settings.
            // Therefore, check beforehand if the event contains interesting knowledge. 
            if (addedElementIds == null && deletedElementIds == null && modifiedElementIds == null)
            {
                return;
            }
            Debug.WriteLine("-- -- -- --");

            var doc = e.GetDocument();

            foreach (var id in addedElementIds)
            {
                var uniqueId = doc.GetElement(id).UniqueId;
                var elemName = doc.GetElement(id)?.Name;
                var ifcGuid = doc.GetElement(id)?.get_Parameter(BuiltInParameter.IFC_GUID);

                if (ifcGuid != null)
                {
                    Debug.WriteLine($"[Transaction Tracker] Elem: >{elemName}< - ADDED: IfcGUID " + ifcGuid.AsString() + " ElementId: " + id);
                }
                else
                {
                    Debug.WriteLine($"[Transaction Tracker] Elem: >{elemName}< - ADDED: NoGUID" + " ElementId: " + id);
                }

                // send event to server
                var msg = new TransactionMessage("ADDED", id.IntegerValue, elemName, uniqueId);
                _connector.PerformPostRequest("/api/ReportTransaction", msg);

            }

            foreach (var id in deletedElementIds)
            {
                var uniqueId = doc.GetElement(id)?.UniqueId;
                var elemName = doc.GetElement(id)?.Name;
                var ifcGuid = doc.GetElement(id)?.get_Parameter(BuiltInParameter.IFC_GUID);

                if (ifcGuid != null)
                {
                    Debug.WriteLine($"[Transaction Tracker] Elem: >{elemName}< - DELETED: IfcGUID " + ifcGuid.AsString() + " ElementId: " + id);
                }
                else
                {
                    Debug.WriteLine($"[Transaction Tracker] Elem: >{elemName}< - DELETED: " + " ElementId: " + id);
                }

                // send event to server
                var msg = new TransactionMessage("DELETED", id.IntegerValue, elemName, uniqueId);
                _connector.PerformPostRequest("/api/ReportTransaction", msg);
            }

            foreach (var id in modifiedElementIds)
            {
                var uniqueId = doc.GetElement(id)?.UniqueId;
                var elemName = doc.GetElement(id)?.Name;
                var ifcGuid = doc.GetElement(id)?.get_Parameter(BuiltInParameter.IFC_GUID);

                if (ifcGuid != null)
                {
                    Debug.WriteLine($"[Transaction Tracker] Elem: >{elemName}< - MODIFIED: IfcGUID: " + ifcGuid.AsString() + " ElementId: " + id);
                }
                else
                {
                    Debug.WriteLine($"[Transaction Tracker] Elem: >{elemName}< - MODIFIED: " +  "ElementId: " + id);
                }

                // send event to server
                var msg = new TransactionMessage("MODIFIED", id.IntegerValue, elemName, uniqueId);
                _connector.PerformPostRequest("/api/ReportTransaction", msg);
            }
            Debug.WriteLine("-- -- -- --");
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        /// <exception cref="NotImplementedException"></exception>
        private void document_created(object sender, DocumentCreatedEventArgs e)
        {
            throw new NotImplementedException();
        }

        #endregion
    }
}