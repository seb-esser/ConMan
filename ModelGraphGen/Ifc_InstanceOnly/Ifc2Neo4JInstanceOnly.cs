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
        private List<Entity> ParseIfcInstanceModel(string fileDirectory)
        {
            var rawIfcEntities = new List<Entity>();

            // Read a text file line by line.
            var lines = File.ReadAllLines(fileDirectory).ToList();
            lines.RemoveAll(s => s.Equals("")); // remove empty lines

            foreach (var line in lines)
                // get schema version
                if (line.StartsWith("FILE_SCHEMA"))
                {
                    var openingPara = line.IndexOf("(", StringComparison.Ordinal);
                    var ifcVersion = line.Substring(openingPara + 3);
                    ifcVersion = ifcVersion.Remove(ifcVersion.Length - 4);
                    ifcVersion = ifcVersion.Replace(" ", string.Empty);
                }

                // parse entities
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
                    var rawIfcEntity = new Entity
                    {
                        EntityId = index,
                        EntityName = entityClass,
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
        private List<AbstractProperty> SplitProperties(string propertyString)
        {
            // init return val 
            var pList = new List<AbstractProperty>();

            // process string
            var rawProps = propertyString.Split(',');


            var i = 0;
            // loop over all properties
            while (i < rawProps.Length)
            {
                var property = rawProps[i];

                // doubleArray Situation!
                if (property.StartsWith("(("))
                {
                    var wrapper = new WrapArrayProperty();

                    // init second iteration var
                    var j = i;
                    while (rawProps[j].EndsWith("))") == false) // find start and end 
                    {
                        j++;
                    }

                    // all properties in the range between i and j are arrays themselves
                    for (int k = i; k <= j; k++)
                    {
                        // identify innerArray
                        var ptArray = new ArrayProperty();

                        // loop inner list
                        do
                        {
                            var simpleVal = new SingleProperty { PVal = rawProps[k] };
                            ptArray.Properties.Add(simpleVal);
                            k++;
                        } while (rawProps[k].EndsWith(")") == false);

                        var lastVal = new SingleProperty {PVal = rawProps[k]};
                        ptArray.Properties.Add(lastVal);

                        wrapper.ArrayProperties.Add(ptArray);
                    }

                    // add wrapperArray to return var
                    pList.Add(wrapper);

                    // set outer counter 
                    i = j + 1;
                }

                // detect a simple arrayProperty
                else if (property.StartsWith("(") == true)
                {
                    // find closing property
                    // init second iteration var
                    var j = i;
                    while (rawProps[j].EndsWith(")") == false)
                    {
                        j++;
                    }

                    // i is the opening one, j is the closing one
                    var arrayProp = new ArrayProperty();
                    for (int k = i; k <= j; k++)
                    {
                        // init new simple property
                        var prop = new SingleProperty {PVal = rawProps[k]};

                        // add to array property
                        arrayProp.Properties.Add(prop);
                    }

                    // add to returning list
                    pList.Add(arrayProp);

                    // finally: set while iterator to j to skip arrayProps
                    i = j + 1;
                }

                // it is a simple property
                else
                {
                    var singleProp = new SingleProperty {PVal = property};

                    // add to returning list
                    pList.Add(singleProp);

                    // increase while criteria
                    i++;
                }
            }
            
            return pList;
        }
    }
}