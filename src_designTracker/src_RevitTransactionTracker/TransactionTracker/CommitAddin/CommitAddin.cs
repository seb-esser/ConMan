using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using Autodesk.Revit.ApplicationServices;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using Newtonsoft.Json;
using Formatting = System.Xml.Formatting;

namespace CommitAddin
{
    [Autodesk.Revit.Attributes.Regeneration(Autodesk.Revit.Attributes.RegenerationOption.Manual)]
    [Autodesk.Revit.Attributes.Transaction(Autodesk.Revit.Attributes.TransactionMode.Manual)]
    public class CommitAddin : IExternalCommand
    {
        /// <summary>
        /// creates a snapshot of all family instances currently used in the Revit model
        /// </summary>
        /// <param name="commandData"></param>
        /// <param name="message"></param>
        /// <param name="elements"></param>
        /// <returns></returns>
        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {

            UIApplication uiapp = commandData.Application;
            UIDocument uidoc = uiapp.ActiveUIDocument;
            Document doc = uidoc.Document;

            try
            {

                FilteredElementCollector coll
                    = new FilteredElementCollector(doc)
                        .WhereElementIsNotElementType();
                var familyInstances = coll.OfClass(typeof(FamilyInstance));

                Debug.WriteLine("count coll: " + coll.Count());

                var trackingBucket = new List<ObjectBucket>(); 

                foreach (var element in familyInstances)
                {
                   
                    // get element id
                    var elementId = element.Id.IntegerValue;

                    // get element UniqueId
                    var objectGuid = element.UniqueId;

                    // get version id
                    var versionGuid = element.VersionGuid.ToString();

                    // get element name
                    var name = element.Name;

                    var bucket = new ObjectBucket(elementId, name, objectGuid, versionGuid);

                    trackingBucket.Add(bucket);

                    
                }

                var snapshot = new Snapshot(trackingBucket); 

                DateTime utcDate = DateTime.UtcNow;
                string fileName = @"C:\Users\ga38hep\dev\" + utcDate.ToShortDateString().Replace(".", "-") + "_" + utcDate.ToLongTimeString().Replace(":", "-") + ".json";
                Debug.WriteLine(fileName);

                using (StreamWriter writeText = new StreamWriter(@fileName))
                {
                    string json = JsonConvert.SerializeObject(snapshot);
                    writeText.Write(json);
                }

            }
            catch (Exception e)
            {
                Console.WriteLine(e);
                Debug.WriteLine(e);
            }

            return Result.Succeeded;
        }


    }
}
