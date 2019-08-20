using System;
using System.Collections.Generic;

namespace ModelGraphGen.Domain
{
    public class RawIfcEntity
    {
        public int EntityId { get; set; }
        public string entityName { get; set; }
        public List<RawIfcProperty> Properties { get; set; }
        
        /// <summary>
        /// Default constructor
        /// </summary>
        public RawIfcEntity()
        {
            Properties = new List<RawIfcProperty>();
        }

        /// <summary>
        /// log content to console
        /// </summary>
        public void ToConsole()
        {
            // log
            Console.WriteLine(EntityId + "   " + entityName);
            foreach (var kvp in Properties)
            {
                string pVal = "";
                if (kvp.PVal_Simple != null)
                {
                    pVal = kvp.PVal_Simple;
                }
                else if (kvp.PVal_Complex != null)
                {
                    pVal = kvp.PVal_Complex;
                }
                Console.WriteLine("     pName = {0}, pVal = {1}", kvp.PName, pVal);
            }
            Console.WriteLine();
        }
    }
}
