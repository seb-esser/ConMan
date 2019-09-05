using System;
using System.Collections.Generic;

namespace ModelGraphGen.Domain
{

    public class Entity
    {
        public int EntityId { get; set; }
        public string EntityName { get; set; }

        // contains both, SingleProperty an ArrayProperty
        public List<AbstractProperty> Properties; 
       

        /// <summary>
        /// Default constructor
        /// </summary>
        public Entity()
        {
                Properties = new List<AbstractProperty>();
        }

        /// <summary>
        /// log content to console
        /// </summary>
        public void ToConsole()
        {
            // log
            Console.WriteLine(EntityId + "\t" + EntityName);
            foreach (var property in Properties)
            {
                switch (property.GetType().Name)
                {
                    case "SingleProperty":
                        // cast
                        var p = property as SingleProperty;

                        // write to console
                        Console.WriteLine("\t Type: SingleProperty \t pName = {0} \t pVal = {1}",  property.PropertyName, p.PVal);
                        break;

                    case "ArrayProperty":
                        // cast
                        var q = property as ArrayProperty;

                        // write to console
                        Console.WriteLine("\t Type: ArrayProperty \t pName = {0}", q.PropertyName);
                        // loop over all contained values
                        foreach (var singleProperty in q.Properties)
                        {
                            Console.WriteLine("\t \t pVal = {0}", singleProperty.PVal);
                        }
                        break;

                    case "WrapArrayProperty":
                        var r = property as WrapArrayProperty;

                        // write to console
                        Console.WriteLine("\t Type: WrapArrayProperty \t pName = {0}", r.PropertyName);
                        // loop over all contained values
                        foreach (ArrayProperty arrayProperty in r.ArrayProperties)
                        {
                            Console.WriteLine("\t \t ArrayProperty");
                            foreach (var singleProperty in arrayProperty.Properties)
                            {
                                Console.WriteLine("\t \t \t pVal = {0}", singleProperty.PVal);
                            }
                            
                        }
                        break;

                    default:
                        Console.WriteLine("Unknown property type was detected. Entity: " + EntityId);
                     break;
                }
            }
            // space to next entity
            Console.WriteLine();
        }
    }
}
