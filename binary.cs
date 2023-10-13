using System;
using System.Reflection;
using System.IO;

class Program
{
    static void Main(string[] args)
    {
        // Read the raw binary data of the executable
        byte[] executableBytes = File.ReadAllBytes("Test.exe");

        // Load and execute the executable from the binary data
        ExecuteExecutableFromBytes(executableBytes);
    }

    static void ExecuteExecutableFromBytes(byte[] executableBytes)
    {
        try
        {
            // Load the executable assembly from the binary data
            Assembly assembly = Assembly.Load(executableBytes);

            // Find and invoke the entry point (e.g., Main method)
            MethodInfo entryPoint = assembly.EntryPoint;
            if (entryPoint != null)
            {
                object[] parameters = entryPoint.GetParameters().Length == 0 ? null : new object[] { new string[0] };
                entryPoint.Invoke(null, parameters);
            }
            else
            {
                Console.WriteLine("No entry point found in the executable.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error executing the executable from bytes: " + ex.Message);
        }
    }
}