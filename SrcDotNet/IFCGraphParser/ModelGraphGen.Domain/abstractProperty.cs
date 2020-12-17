using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ModelGraphGen.Domain
{
    /// <summary>
    /// Abstract superclass of ArrayProperty and SingleProperty
    /// </summary>
    public abstract class AbstractProperty
    {
        public string PropertyName { get; set; }
    }
}
