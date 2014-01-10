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
	private String hostname = null, neuid = null;
	private int port = 27993;
	private boolean useSSL = false;
	private String cert_path = System.getProperty("user.dir") + "/jssecacerts";

	public static void main(String[] args) {
		Client client = new Client();
		client.config(args);
		client.run();
	}

	/**
	 *
	 * @param args
	 */
	private void config(String[] args) {
		if(args.length < 2 || args.length > 5){
			System.err.println("Illegal Arguments.");
			System.exit(1);
		} else if(args.length == 2){//[hostname] [NEU ID]
			hostname = args[0];
			neuid = args[1];
		} else if(args.length == 3){//-s [hostname] [NEU ID]
			useSSL = true;
			System.setProperty("javax.net.ssl.trustStore", cert_path);
			port = 27994;
			hostname = args[1];
			neuid = args[2];
		} else if(args.length == 4){//-p port [hostname] [NEU ID]
			port = Integer.parseInt(args[1]);
			hostname = args[2];
			neuid = args[3];
		} else if(args.length == 5){//-p port -s [hostname] [NEU ID]
			port = Integer.parseInt(args[1]);
			useSSL = true;
			System.setProperty("javax.net.ssl.trustStore", cert_path);
			hostname = args[2];
			neuid = args[3];
		}
	}

	/**
	 *
	 */
	private void run() {
		PrintWriter out;
		BufferedReader in;
		Socket socket;
		try {
			if(useSSL){
				SSLSocketFactory factory = (SSLSocketFactory) SSLSocketFactory.getDefault();
			    socket = (SSLSocket) factory.createSocket(hostname, port);
			}else
			{
				socket = new Socket(hostname, port);
			}

			out = new PrintWriter(socket.getOutputStream(), true);
			in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
			out.println("cs5700spring2014 HELLO " + neuid + "\n");
			out.flush();

			String message = in.readLine();
			while (message.contains("STATUS")) {
				System.out.println("[DEBUG]STATUS:" + message);
				int result = getResult(message);
				System.out.println("[DEBUG]SOLUTION:" + "cs5700spring2014 " + result + "\n");

				out.println("cs5700spring2014 " + result + "\n");
				out.flush();
				message = in.readLine();
			}

			System.out.println("[DEBUG]Bye:" + message);
			System.out.println(getSecretFlag(message));

			in.close();
			out.close();
			socket.close();

		} catch (UnknownHostException e) {
			System.err.println("Don't know about host " + hostname);
			System.exit(1);
		} catch (IOException e) {
			e.printStackTrace();
			System.err.println("Couldn't get I/O for the connection to "
					+ hostname);
			System.exit(1);
		}
	}

	/**
	 *
	 * @param message
	 * @return
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
	 *
	 * @param message
	 * @return
	 */
	private static String getSecretFlag(String message) {
		StringTokenizer st = new StringTokenizer(message);
		st.nextToken();
		return st.nextToken();
	}
}
