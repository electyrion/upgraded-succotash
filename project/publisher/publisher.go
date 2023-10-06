package main

// CLIENT

import (
	"fmt"
	"bufio"
    "context"
    "crypto/tls"
    "log"
    "net"
    "os"

    "github.com/quic-go/quic-go"

	"jarkom.cs.ui.ac.id/h01/project/utils"
)

const (
    serverIP          = "34.171.103.191"
    serverPort        = "9906"
    serverType        = "udp4"
    bufferSize        = 2048
    appLayerProto     = "lrt-jabodebek-2106750906"
    sslKeyLogFileName = "ssl-key.log"
)

func main() {
	sslKeyLogFile, err := os.Create(sslKeyLogFileName)
    if err != nil {
        log.Fatalln(err)
    }
    defer sslKeyLogFile.Close()

    fmt.Printf("QUIC Client Socket Program Example in Go\n")

    tlsConfig := &tls.Config{
        InsecureSkipVerify: true,
        NextProtos:         []string{appLayerProto},
        KeyLogWriter:       sslKeyLogFile,
    }
    connection, err := quic.DialAddr(context.Background(), net.JoinHostPort(serverIP, serverPort), tlsConfig, &quic.Config{})
    if err != nil {
        log.Fatalln(err)
    }

    defer connection.CloseWithError(0x0, "No Error")

    fmt.Printf("[quic] Dialling from %s to %s\n", connection.LocalAddr(), connection.RemoteAddr())

    fmt.Printf("[quic] Creating receive buffer of size %d\n", bufferSize)
    receiveBuffer := make([]byte, bufferSize)

	
	destination := "Harjamukti"
	
	packetA := utils.LRTPIDSPacket{
		LRTPIDSPacketFixed: utils.LRTPIDSPacketFixed{
			TransactionId:     0x55,
			IsAck:             false,
			IsNewTrain:        false,
			IsUpdateTrain:     false,
			IsDeleteTrain:     false,
			IsTrainArriving:   true,
			IsTrainDeparting:  false,
			TrainNumber:       42,
			DestinationLength: uint8(len(destination)),
		},
		Destination: destination,
	}
	resultA := utils.Encoder(packetA)
	// fmt.Println(resultA)
	// fmt.Println(utils.Decoder(resultA))


	packetB := utils.LRTPIDSPacket{
		LRTPIDSPacketFixed: utils.LRTPIDSPacketFixed{
			TransactionId:     0x55,
			IsAck:             false,
			IsNewTrain:        false,
			IsUpdateTrain:     false,
			IsDeleteTrain:     false,
			IsTrainArriving:   false,
			IsTrainDeparting:  true,
			TrainNumber:       42,
			DestinationLength: uint8(len(destination)),
		},
		Destination: destination,
	}
	resultB := utils.Encoder(packetB)
	// fmt.Println(resultB)
	// fmt.Println(utils.Decoder(resultB))



	streamA, err := connection.OpenStreamSync(context.Background())
	if err != nil {
		log.Fatalln(err)
	}
	fmt.Printf("[quic] Opened bidirectional stream %d to %s\n", streamA.StreamID(), connection.RemoteAddr())

	streamB, err := connection.OpenStreamSync(context.Background())
	if err != nil {
		log.Fatalln(err)
	}
	fmt.Printf("[quic] Opened bidirectional stream %d to %s\n", streamB.StreamID(), connection.RemoteAddr())

	go func() {
		fmt.Printf("[quic] [Stream ID: %d] Sending message '%s'\n", streamA.StreamID(), resultA)
		_, err = streamA.Write([]byte(resultA))
		if err != nil {
			log.Fatalln(err)
		}
		fmt.Printf("[quic] [Stream ID: %d] Message sent\n", streamA.StreamID())
	}

	go func() {
		fmt.Printf("[quic] [Stream ID: %d] Sending message '%s'\n", streamB.StreamID(), resultB)
		_, err = streamB.Write([]byte(resultB))
		if err != nil {
			log.Fatalln(err)
		}
		fmt.Printf("[quic] [Stream ID: %d] Message sent\n", streamB.StreamID())
	}

	// capture message packetA from server
	receiveLength, err := streamA.Read(receiveBuffer)
	if err != nil {
		log.Fatalln(err)
	}
	fmt.Printf("[quic] [Stream ID: %d] Received %d bytes of message from server\n", streamA.StreamID(), receiveLength)

	response := receiveBuffer[:receiveLength]
	fmt.Printf("[quic] [Stream ID: %d] Received message: '%s'\n", streamA.StreamID(), response)


	// capture message packetB from server
	receiveLength, err = streamB.Read(receiveBuffer)
	if err != nil {
		log.Fatalln(err)
	}
	fmt.Printf("[quic] [Stream ID: %d] Received %d bytes of message from server\n", streamB.StreamID(), receiveLength)

	response = receiveBuffer[:receiveLength]
	fmt.Printf("[quic] [Stream ID: %d] Received message: '%s'\n", streamB.StreamID(), response)
}
