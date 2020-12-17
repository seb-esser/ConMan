using System;
using System.Collections.Generic;
using ModelGraphGen.Domain;
using Neo4j.Driver;

namespace ModelGraphGen.ScriptGenerator
{
    public class IfcToGraph : IScriptGenerator
    {
        public static string GenerateNeo4JGraph(List<Entity> instanceData)
        {
            var neo4jScript = "CREATE ";

            // build entities
            foreach (var entity in instanceData)
            {
               neo4jScript += BuildEntity(entity);
            }

            // build relationships and properties
            foreach (var entity in instanceData)
            {
                neo4jScript += BuildUnknownRelationships(entity);
            }
            return neo4jScript;
        }
        

        public void GenerateGrGenGraph()
        {
            throw new System.NotImplementedException();
        }

        public void GenerateNeo4JGraph()
        {
            throw new System.NotImplementedException();
        }

        private static string BuildEntity(Entity entity)
        {
            string fragment; 
            if (entity.EntityName.StartsWith("IfcRel"))
            {
                fragment = "(objRel" + entity.EntityId + ":IfcEntity" +
                           "{EntityNr: " + entity.EntityId + ", "
                           + "EntityName: " + "'" + entity.EntityName + "'"
                           + "}), ";
            }
            else
            {
                fragment = "(Entity" + entity.EntityId + ":IfcEntity" +
                               "{EntityNr: " + entity.EntityId + ", "
                               + "EntityName: " + "'" + entity.EntityName + "'"
                               + "}), ";
            }

           
            return fragment;
        }

        private static string BuildUnknownRelationships(Entity entity)
        {
            // init Cypher statement
            var fragment = "";

            // loop over all properties of the current entity
            foreach (var property in entity.Properties)
            {
                switch (property.GetType().Name)
                {
                    case "SingleProperty":
                        // cast
                        var p = property as SingleProperty;

                        if (p.PVal.StartsWith("#"))
                        {
                            // build a relationship
                            fragment += " (`n" + entity.EntityId + "`)-[:`UnknownRel` ]->(`n" + p.PVal.Substring(1, p.PVal.Length -1) +"`), ";
                        }
                        else
                        {
                            // property is an attribute of the entity
                            //fragment += p.PropertyName + ":" + p.PVal + ", ";
                        }


                        break;

                    case "ArrayProperty":
                        // cast
                        var q = property as ArrayProperty;

                        foreach (var singleProperty in q.Properties)
                        {
                            fragment += " (`n" + entity.EntityId + "`)-[:`UnknownRel`]->(`n" + singleProperty.PVal + "`), ";
                        }

                        break;

                    case "WrapArrayProperty":
                        var r = property as WrapArrayProperty;

                        //// write to console
                        
                        //// loop over all contained values
                        //foreach (ArrayProperty arrayProperty in r.ArrayProperties)
                        //{
                        //    //Console.WriteLine("\t \t ArrayProperty");
                        //    foreach (var singleProperty in arrayProperty.Properties)
                        //    {
                        //        //Console.WriteLine("\t \t \t pVal = {0}", singleProperty.PVal);
                        //    }

                        //}

                        break;

                 
                }
            }

            return fragment; 
        }
    }
}