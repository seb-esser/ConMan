using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using ModelGraphGen.Domain;

namespace ModelGraphGen.Ifc_InstanceOnly
{
    /// <summary>
    /// </summary>
    internal class Ifc2Neo4JInstanceOnly : IParser
    {
        /// <summary>
        /// </summary>
        /// <param name="FileDirectory"></param>
        /// <returns></returns>
        public string Parse(string FileDirectory)
        {
            var rawData = ParseIfcInstanceModel(FileDirectory);

            return "ResultingScript";
        }

        /// <summary>
        ///     Loads an Ifc instance model and prepares the contained data for further processing
        /// </summary>
        /// <param name="fileDirectory">Full Path to *.ifc file</param>
        private List<RawIfcEntity> ParseIfcInstanceModel(string fileDirectory)
        {
            var rawIfcEntities = new List<RawIfcEntity>();

            // Read a text file line by line.
            var lines = File.ReadAllLines(fileDirectory).ToList();
            lines.RemoveAll(s => s.Equals("") );    // remove empty lines

            foreach (var line in lines)
                // get schema version
                if (line.StartsWith("FILE_SCHEMA"))
                {
                    var openingPara = line.IndexOf("(", StringComparison.Ordinal);
                    var ifcVersion = line.Substring(openingPara + 3);
                    ifcVersion = ifcVersion.Remove(ifcVersion.Length - 4);
                    ifcVersion = ifcVersion.Replace(" ", string.Empty);
                }

                else if (line[0] == '#') // no comment, nothing else
                {
                    // Get correct keyWord/IfcClass name
                    var equalSign = line.IndexOf("=", StringComparison.Ordinal);

                    // Get and split properties
                    var propertyOpen = line.IndexOf("(", StringComparison.Ordinal);

                    // get entity number
                    var index = int.Parse(line.Substring(1, equalSign - 1));

                    // get entityClass
                    var entityClass = line.Substring(equalSign + 1, propertyOpen - equalSign - 1);

                    // separate all Properties - comma separated
                    var propertyString = line.Substring(propertyOpen);
                    propertyString = propertyString.Remove(0, 1); // cut opening parenthesis 
                    propertyString = propertyString.Remove(propertyString.Length - 2, 2); // cut closing parenthesis 

                    // split params
                    var properties = SplitProperties(propertyString);

                    // setup storage
                    var rawIfcEntity = new RawIfcEntity
                    {
                        EntityId = index,
                        entityName = entityClass,
                        Properties = properties
                    };

                    // add to storage
                    rawIfcEntities.Add(rawIfcEntity);

                    // log to console
                    rawIfcEntity.ToConsole();
                }

            return rawIfcEntities;
        }

        /// <summary>
        /// Splits given Properties of Ifc Instance Model
        /// </summary>
        /// <param name="propertyString"></param>
        /// <returns></returns>
        private List<RawIfcProperty> SplitProperties(string propertyString)
        {
            // init return val 
            var pList = new List<RawIfcProperty>();

            // process string
            var splittedProps = propertyString.Split(',');
            foreach (var prop in splittedProps) // process each prop
            {
                var myProperty = new RawIfcProperty();

                if (prop.StartsWith("(")) // sub-property ahead!
                {
                    myProperty.PVal_Reference = prop;
                }
                else if (prop.StartsWith("#")) // reference
                {
                    myProperty.PVal_Reference = prop;
                }

                else
                {
                    myProperty.PVal_Normal = prop;
                }


                pList.Add(myProperty);
            }


            return pList;
        }
    }
}