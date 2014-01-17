import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.StringTokenizer;

import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;

public class Client {
	private String hostname, neuid;
	// TCP port, default is 27993
	private int port = 27993;
	//whether use SSL encrypted connection, default is false
	private boolean useSSL = false;
	//the path of jssecacerts file
	private String cert_path = System.getProperty("user.dir") + "/jssecacerts";

public static void main(String[] args) {
		Client client = new Client();
		client.config(args);
		client.run();
	}

	/**
	 * Configure arguments
	 * @param args
	 */
	private void config(String[] args) {
		if(args.length < 2 || args.length > 5){
			System.err.println("Illegal Arguments.");
			System.exit(1);
		}
		if(findArgument(args, "-s") != -1){
			useSSL = true;
			System.setProperty("javax.net.ssl.trustStore", cert_path);
			port = 27994;
		}
		if(findArgument(args, "-p") != -1){
			int index = findArgument(args, "-p");
			port = Integer.parseInt(args[++index]);
		}
		hostname = args[args.length - 2];
		neuid = args[args.length - 1];
	}

	@Override
	public String toString(){
		StringBuilder sb = new StringBuilder();
		sb.append("Use SSL: " + useSSL);
		sb.append("\nPort: " + port);
		sb.append("\nHost name: " + hostname);
		sb.append("\nNEU ID: " + neuid);
		return sb.toString();
	}

	/**
	 * Returns the index of the first occurrence of the specified option in args,
	 * or -1 if args does not contain the option.
	 * @param args the given argument list
	 * @param option the specified option
	 * @return -1 if there is no <code>option</code> in <code>args</code>.<pre></pre>
	 *         the index of the first occurrence of the <code>option</code> in <code>args</code>.
	 */
	private int findArgument(String[] args, String option){
		int index = -1;
		for(int i = 0; i < args.length; i++)
			if(args[i].equals(option))
				index = i;
		return index;
	}

	/**
	 * Run client program
	 */
	private void run() {
		PrintWriter out;
		BufferedReader in;
		Socket socket;
		//Create specified socket
		try {
			if(useSSL){
				SSLSocketFactory factory = (SSLSocketFactory) SSLSocketFactory.getDefault();
			    socket = (SSLSocket) factory.createSocket(hostname, port);
			}else
			{
				socket = new Socket(hostname, port);
			}

			// Send HELLO message
			out = new PrintWriter(socket.getOutputStream(), true);
			in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
			out.println("cs5700spring2014 HELLO " + neuid + "\n");
			out.flush();

			// Receive STATUS message
			String message = in.readLine();
			while (message.contains("STATUS")) {
				//System.out.println("[DEBUG]STATUS:" + message);
				int result = getResult(message);
				//System.out.println("[DEBUG]SOLUTION:" + "cs5700spring2014 " + result + "\n");
				//Send SOLUTION message
				out.println("cs5700spring2014 " + result + "\n");
				out.flush();
				// Receive Bye message or another STATUS message
				message = in.readLine();
			}

			//System.out.println("[DEBUG]Bye:" + message);
			System.out.println(getSecretFlag(message));
			//Close IO and connection
			in.close();
			out.close();
			socket.close();

		} catch (UnknownHostException e) {
			System.err.println("Don't know about host " + hostname);
			System.exit(1);
		} catch (IOException e) {
			e.printStackTrace();
			System.err.println("Couldn't get I/O for the connection to " + hostname);
			System.exit(1);
		}
	}

	/**
	 * Parse STATUS message and compute the mathematical expression in message
	 * @param message STATUS message
	 * @return result of the mathematical expression
	 */
	private static int getResult(String message) {
		int num1 = 0, num2 = 0, res = 0;
		String operator = null;
		StringTokenizer st = new StringTokenizer(message);
		st.nextToken();
		st.nextToken();
		num1 = Integer.parseInt(st.nextToken());
		operator = st.nextToken();
		num2 = Integer.parseInt(st.nextToken());
		if (operator.equals("+"))
			res = num1 + num2;
		else if (operator.equals("-"))
			res = num1 - num2;
		else if (operator.equals("*"))
			res = num1 * num2;
		else if (operator.equals("/"))
			res = num1 / num2;
		return res;
	}

	/**
	 * Parse BYE message and get secret flag in message
	 * @param message BYE message
	 * @return secret flag
	 */
	private static String getSecretFlag(String message) {
		StringTokenizer st = new StringTokenizer(message);
		st.nextToken();
		return st.nextToken();
	}
}
