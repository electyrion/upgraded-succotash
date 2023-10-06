package main

// SERVER, PIDS, VM2

import (
	"fmt"
	"context"
    "crypto/tls"
    "io"
    "log"
    "net"

    "github.com/quic-go/quic-go"

	"jarkom.cs.ui.ac.id/h01/project/utils"
)

const (
    serverIP      = ""
    serverPort    = "9906"
    serverType    = "udp4"
    bufferSize    = 2048
    appLayerProto = "lrt-jabodebek-2106750906"
)

func Handler(packet utils.LRTPIDSPacket) string {
	var result string

	if (packet.LRTPIDSPacketFixed.IsTrainArriving) {
		result = "Mohon perhatian, kereta tujuan " + string(packet.Destination) + " akan tiba di Peron 1"
	} else if (packet.LRTPIDSPacketFixed.IsTrainDeparting) {
		result = "Mohon perhatian, kereta tujuan " + string(packet.Destination) + " akan diberangkatkan dari Peron 1"
	}
	
	return result
}

func main() {
	localUdpAddress, err := net.ResolveUDPAddr(serverType, net.JoinHostPort(serverIP, serverPort))
	if err != nil {
		log.Fatalln(err)
	}
	socket, err := net.ListenUDP(serverType, localUdpAddress)
	if err != nil {
		log.Fatalln(err)
	}

	defer socket.Close()

	fmt.Printf("QUIC Server Socket Program Example in Go\n")
	fmt.Printf("[%s] Preparing UDP listening socket on %s\n", serverType, socket.LocalAddr())

	tlsConfig := &tls.Config{
		Certificates: utils.GenerateTLSSelfSignedCertificates(),
		NextProtos:   []string{appLayerProto},
	}
	listener, err := quic.Listen(socket, tlsConfig, &quic.Config{})
	if err != nil {
		log.Fatalln(err)
	}

	defer listener.Close()

	fmt.Printf("[quic] Listening QUIC connections on %s\n", listener.Addr())

	for {
		connection, err := listener.Accept(context.Background())
		if err != nil {
			log.Fatalln(err)
		}

		go handleConnection(connection)
	}
}

func handleConnection(connection quic.Connection) {
    fmt.Printf("[quic] Receiving connection from %s\n", connection.RemoteAddr())

    streamA, err := connection.AcceptStream(context.Background())
    if err != nil {
        log.Fatalln(err)
    }
    go handleStream(connection.RemoteAddr(), streamA)

    streamB, err := connection.AcceptStream(context.Background())
    if err != nil {
        log.Fatalln(err)
    }
    go handleStream(connection.RemoteAddr(), streamB)
}

func handleStream(clientAddress net.Addr, stream quic.Stream) {
    fmt.Printf("[quic] [Client: %s] Receive stream open request with ID %d\n", clientAddress, stream.StreamID())

    _, err := io.Copy(logicProcessorAndWriter{stream}, stream)
    if err != nil {
        fmt.Println(err)
    }
}

type logicProcessorAndWriter struct { io.Writer }

func (lw logicProcessorAndWriter) Write(receivedMessageRaw []byte) (int, error) {
	receivedMessage := utils.Decoder(receivedMessageRaw)
	fmt.Printf("[quic] Receive Packet: %+v\n", receivedMessage)

	response := Handler(receivedMessage)

	receivedMessage.LRTPIDSPacketFixed.IsAck = true
	responseMessage := utils.Encoder(receivedMessage)
	writeLength, err := lw.Writer.Write([]byte(responseMessage))

	fmt.Printf("[quic] Send message: %s\n", response)

	return writeLength, err
}
