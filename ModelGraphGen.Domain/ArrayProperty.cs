using System.Collections.Generic;

namespace ModelGraphGen.Domain
{
    /// <summary>
    /// Used to parse any Ifc property which is composed by a list
    /// </summary>
    public class ArrayProperty : AbstractProperty
    {
        public List<SingleProperty> Properties;

        
        /// <summary>
        /// Default constructor
        /// </summary>
        public ArrayProperty()
        {
            Properties = new List<SingleProperty>();
        }
    }
}
