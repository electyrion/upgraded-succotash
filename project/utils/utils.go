package utils

import (
	"bytes"
	"bufio"
	"crypto/rand"
	"crypto/rsa"
	"crypto/tls"
	"crypto/x509"
	"encoding/pem"
	"io"
	"log"
	"math/big"
	"encoding/binary"
)

// Tipe data komponen boleh diubah, namun variabelnya jangan diubah
type LRTPIDSPacketFixed struct {
	TransactionId     uint16
	IsAck             bool
	IsNewTrain        bool
	IsUpdateTrain     bool
	IsDeleteTrain     bool
	IsTrainArriving   bool
	IsTrainDeparting  bool
	TrainNumber       uint16
	DestinationLength uint8
}

type LRTPIDSPacket struct {
	LRTPIDSPacketFixed
	Destination string
}

func Encoder(packet LRTPIDSPacket) []byte {
	buffer := new(bytes.Buffer)

	binary.Write(buffer, binary.BigEndian, packet.LRTPIDSPacketFixed)
	buffer.WriteString(packet.Destination)

	return buffer.Bytes()
}

func Decoder(rawMessage []byte) LRTPIDSPacket {

	var decodedFixedSegment LRTPIDSPacketFixed
	bytesReader := bytes.NewReader(rawMessage)
	binary.Read(bytesReader, binary.BigEndian, &decodedFixedSegment)

	destinationStringRaw := make([]byte, decodedFixedSegment.DestinationLength)
	bytesReader.Read(destinationStringRaw)

	return LRTPIDSPacket {
		LRTPIDSPacketFixed: decodedFixedSegment,
		Destination: string(destinationStringRaw),	
	}
}


type qlogWriter struct {
	*bufio.Writer
	io.Closer
}

func GenerateTLSSelfSignedCertificates() []tls.Certificate {
	key, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		log.Fatalln(err)
	}
	template := x509.Certificate{SerialNumber: big.NewInt(1)}
	certDER, err := x509.CreateCertificate(rand.Reader, &template, &template, &key.PublicKey, key)
	if err != nil {
		log.Fatalln(err)
	}

	keyPEM := pem.EncodeToMemory(&pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(key)})
	certPEM := pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: certDER})

	tlsCert, err := tls.X509KeyPair(certPEM, keyPEM)
	if err != nil {
		log.Fatalln(err)
	}
	return []tls.Certificate{tlsCert}
}