using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Diagnostics;
using System.Linq;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Analysis;
using Autodesk.Revit.DB.Events;
using Autodesk.Revit.Exceptions;
using Autodesk.Revit.UI;
using ApplicationException = Autodesk.Revit.Exceptions.ApplicationException;

namespace TransactionTracker
{
    public class TransactionTrackerClass : IExternalApplication
    {
        #region Properties

        readonly ServerConnector _connector = new ServerConnector();
        private List<ElementCopy> _elementCopies = new List<ElementCopy>();


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

                application.ControlledApplication.DocumentClosed +=
                    new EventHandler<Autodesk.Revit.DB.Events.DocumentClosedEventArgs>(application_DocumentClosed);

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
            // remove the events
            application.ControlledApplication.DocumentOpened -= application_DocumentOpened; 
            application.ControlledApplication.DocumentClosed -= application_DocumentClosed;
            application.ControlledApplication.DocumentSaved -= application_DocumentSaved;
            application.ControlledApplication.DocumentChanged -= document_changed;
            application.ControlledApplication.DocumentCreated -= document_created;

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

                FilteredElementCollector coll = new FilteredElementCollector(doc).WherePasses(
                    new LogicalOrFilter(
                    new ElementIsElementTypeFilter(false),
                    new ElementIsElementTypeFilter(true))
                );

                Debug.WriteLine("count coll: " + coll.Count());

                foreach (var element in coll)
                {
                    _elementCopies.Add(new ElementCopy(element));
                }


            }
            catch (Exception e)
            {
                Console.WriteLine(e);
                Debug.WriteLine(e);
            }
        }

        private void application_DocumentClosed(object sender, DocumentClosedEventArgs e)
        {

            // clear list on plugin level 
            _elementCopies.Clear();
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

            var msgCollection = new TransactionMsgBundle();

            if (addedElementIds == null && deletedElementIds == null && modifiedElementIds == null)
            {
                return;
            }
            Debug.WriteLine("-- -- -- --");

            var doc = e.GetDocument();

            foreach (var id in addedElementIds)
            {
                var elem = doc.GetElement(id);

                var uniqueId = elem.UniqueId;
                var elemName = elem?.Name;
                var ifcGuid = elem?.get_Parameter(BuiltInParameter.IFC_GUID);

                if (ifcGuid != null)
                {
                    Debug.WriteLine($"[Transaction Tracker] Elem: >{elemName}< - ADDED: IfcGUID " + ifcGuid.AsString() + " ElementId: " + id);
                }
                else
                {
                    Debug.WriteLine($"[Transaction Tracker] Elem: >{elemName}< - ADDED: NoGUID" + " ElementId: " + id);
                }

                // send event to server
                var msg = new TransactionMessage("ADDED", id.IntegerValue, elemName, uniqueId, ifcGuid?.AsString());
                msgCollection.AddMessage(msg);

                // write to shadow
                _elementCopies.Add(new ElementCopy(elem));
            }

            foreach (var id in deletedElementIds)
            {
                var elem = doc.GetElement(id);
                var elemCopy = _elementCopies.Find(a => a.id == id.IntegerValue);

                var uniqueId = elem?.UniqueId;
                if (uniqueId == null)
                {
                    uniqueId = elemCopy?.uniqueId;
                }
                if (uniqueId == null)
                {
                    uniqueId = "n/a";
                }

                var elemName = elem?.Name;
                if (elemName == null)
                {
                    elemName = elemCopy?.name;
                }
                if (elemName == null)
                {
                    elemName = "n/a";
                }

                var ifcGuid = elem?.get_Parameter(BuiltInParameter.IFC_GUID);

                if (ifcGuid != null)
                {
                    Debug.WriteLine($"[Transaction Tracker] Elem: >{elemName}< - DELETED: IfcGUID " + ifcGuid.AsString() + " ElementId: " + id);
                }
                else
                {
                    Debug.WriteLine($"[Transaction Tracker] Elem: >{elemName}< - DELETED: " + " ElementId: " + id);
                }

                // send event to server
                var msg = new TransactionMessage("DELETED", id.IntegerValue, elemName, uniqueId, ifcGuid?.AsString());
                msgCollection.AddMessage(msg);

                // write update to shadow
                var elementCopies = _elementCopies.RemoveAll(a=>a.id == id.IntegerValue);
                if (elementCopies > 1)
                {
                    throw new Exception("Deleted more than one Element. ");
                }
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
                var msg = new TransactionMessage("MODIFIED", id.IntegerValue, elemName, uniqueId, ifcGuid?.AsString()); 
                msgCollection.AddMessage(msg);
                
            }


            _connector.PerformPostRequest("/api/ReportTransaction", msgCollection);
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
            // get document from event args.
            Document doc = e.Document;

            FilteredElementCollector coll = new FilteredElementCollector(doc).WherePasses(
                new LogicalOrFilter(
                    new ElementIsElementTypeFilter(false),
                    new ElementIsElementTypeFilter(true))
            );

            Debug.WriteLine("count coll: " + coll.Count());

            // add to shadow list 
            foreach (var element in coll)
            {
                _elementCopies.Add(new ElementCopy(element));
            }
        }

        #endregion
    }
}