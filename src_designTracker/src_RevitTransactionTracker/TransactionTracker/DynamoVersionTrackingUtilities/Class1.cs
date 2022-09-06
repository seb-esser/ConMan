using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.DesignScript.Runtime;
using CommitAddin;
using JsonDiffPatchDotNet;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace DynamoVersionTrackingUtilities
{
    public class BucketLoader
    {
        [IsVisibleInDynamoLibrary(false)]
        internal BucketLoader()
        {

        }
        
        /// <summary>
        /// 
        /// </summary>
        /// <returns></returns>
        [MultiReturn(new[] { "insertedElementIds", "removedElementIds", "modifiedElementIds"})]
        public static Dictionary<string, object> LoadSnapshots(string snapshotPathInit, string snapshotPathUpdated)
        {

            JObject initialSnapshot;
            JObject updatedSnapshot;

            using (StreamReader reader = new StreamReader(@snapshotPathInit))
            {
                var raw = reader.ReadToEnd();
                initialSnapshot = JObject.Parse(raw);
            }

            using (StreamReader reader = new StreamReader(@snapshotPathUpdated))
            {
                var raw = reader.ReadToEnd();
                updatedSnapshot = JObject.Parse(raw);
            }

            var jdp = new JsonDiffPatch();

            JToken result = jdp.Diff(initialSnapshot, updatedSnapshot);
            Debug.WriteLine(result.ToString());
            

            var insertedIds = new List<int>();
            var removedIds = new List<int>();
            var modifiedIds = new List<int>();

            return new Dictionary<string, object>
            {
                {"insertedElementIds", insertedIds},
                {"removedElementIds", removedIds},
                {"modifiedElementIds", modifiedIds}
            }; ;
        }

    }
}
