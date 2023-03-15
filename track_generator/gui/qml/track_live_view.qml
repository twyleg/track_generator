// Copyright (C) 2023 twyleg
import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15

Window {
	id: window

	width: 1280
	height: 720
	visible: true

	Image {
		id: img

		fillMode: Image.PreserveAspectFit
		anchors.fill: parent
		cache: false
		source: model.filename
		sourceSize.height: height
		sourceSize.width: width

		width: parent.width
		height: parent.height

		function reload() {
			console.log('Reloading image!')
			source = ""
			source = model.filename
		}
	}

	Connections {
		target: model

		function onReloadImage() {
			img.reload()
		}
	}

}
