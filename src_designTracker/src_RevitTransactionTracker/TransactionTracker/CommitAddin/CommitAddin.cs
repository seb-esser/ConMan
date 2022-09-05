using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using Autodesk.Revit.ApplicationServices;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;

namespace CommitAddin
{
    [Autodesk.Revit.Attributes.Regeneration(Autodesk.Revit.Attributes.RegenerationOption.Manual)]
    [Autodesk.Revit.Attributes.Transaction(Autodesk.Revit.Attributes.TransactionMode.Manual)]
    public class CommitAddin : IExternalCommand
    {
        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {

            UIApplication uiapp = commandData.Application;
            UIDocument uidoc = uiapp.ActiveUIDocument;
            Application app = uiapp.Application;
            Document doc = uidoc.Document;

            try
            {
                //FilteredElementCollector coll = new FilteredElementCollector(doc).WherePasses(
                //    new LogicalOrFilter(
                //        new ElementIsElementTypeFilter(false),
                //        new ElementIsElementTypeFilter(true))
                //);
                FilteredElementCollector coll
                    = new FilteredElementCollector(doc)
                        .WhereElementIsNotElementType();
                var familyInstances = coll.OfClass(typeof(FamilyInstance));

                Debug.WriteLine("count coll: " + coll.Count());

                var tracking = new List<string>(); 

                foreach (var element in familyInstances)
                {
                    // get element id
                    var elementId = element.Id;

                    // get element UniqueId
                    var objectGuid = element.UniqueId;

                    // get version id
                    var versionGuid = element.VersionGuid;

                    // get element name
                    var name = element.Name;

                    tracking.Add($"{objectGuid} \t {versionGuid} \t {name} \t {elementId}");

                    
                }

                DateTime utcDate = DateTime.UtcNow;
                string fileName = @"C:\Users\ga38hep\dev\" + utcDate.ToShortDateString().Replace(".", "-") + "_" + utcDate.ToShortTimeString().Replace(":", "-") + ".txt";
                Debug.WriteLine(fileName);

                using (StreamWriter writeText = new StreamWriter(@fileName))
                {
                    foreach (var t in tracking)
                    {
                        writeText.WriteLine(t);
                    }

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
